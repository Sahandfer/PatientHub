from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import Field, create_model
from typing import Any, Dict, List, Literal

from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model

PARADIGMS = {"binary", "scalar", "categorical", "extraction"}


@dataclass
class LLMJudgeEvaluatorConfig(APIModelConfig):
    """Configuration for LLM as a Judge Evaluator."""

    agent_type: str = "llm_judge"
    prompt_path: str = "data/prompts/evaluator/client/classification.yaml"
    target: str = "client"
    eval_type: str = "categorical"
    granularity: str = "session"  # "turn", "turn_by_turn" or "session"
    use_reasoning: bool = False


class LLMJudgeEvaluator:
    """Evaluates conversations using an LLM as a judge."""

    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(configs)
        self.instructions = load_prompts(path=configs.prompt_path, lang=configs.lang)
        if configs.eval_type not in PARADIGMS:
            raise ValueError(
                f"Unsupported eval_type: {configs.eval_type}. Must be one of {PARADIGMS}"
            )
        self.dimensions = self._build_schema()

    def _build_binary_field(self, data: Dict) -> Dict[str, Any]:
        name, ftype = "label", bool
        kwargs = {"description": data.get("description", "True if aspect is present")}
        return {name: (ftype, Field(..., **kwargs))}

    def _build_scalar_field(self, data: Dict) -> Dict[str, Any]:
        name, ftype = "score", int
        min_val, max_val = data.get("range", [1, 5])
        kwargs = {
            "ge": min_val,
            "le": max_val,
            "description": data.get("description", "Rating for this aspect"),
        }
        return {name: (ftype, Field(..., **kwargs))}

    def _build_categorical_field(self, data: Dict) -> Dict[str, Any]:
        labels = tuple(data.get("labels", ["good", "average", "bad"]))
        name, ftype = "label", Literal[labels]
        kwargs = {"description": data.get("description", "Assigned label")}
        return {name: (ftype, Field(..., **kwargs))}

    def _build_extraction_field(self, data: Dict) -> Dict[str, Any]:
        name, ftype = "extracted_passages", List[str]
        kwargs = {"description": data.get("description", "Relevant passages")}
        return {name: (ftype, Field(..., **kwargs))}

    def _build_field(self, data: Dict) -> Dict[str, Any]:
        field_builder = getattr(self, f"_build_{self.configs.eval_type}_field")
        fields = field_builder(data)
        if self.configs.use_reasoning:
            fields["reasoning"] = (
                str,
                Field(
                    ...,
                    description="Your short explanation/reasoning for this judgment (1-2 sentences)",
                ),
            )

        return fields

    def _build_aspect(self, aspect: Dict) -> Any:
        fields = self._build_field(data=aspect)
        return create_model(aspect["name"], **fields)

    def _build_dimension(self, dim: Dict):
        fields = {}
        aspects = dim.get("aspects", [])
        if not aspects:
            fields = self._build_field(data=dim)
            return create_model(dim["name"], **fields)

        inherit_keys = {
            k: v for k, v in dim.items() if k not in {"name", "description", "aspects"}
        }

        fields = {}
        for aspect in aspects:
            # Inherit keys from dimension (e.g., range, labels)
            merged_aspect = {**inherit_keys, **aspect}
            aspect_model = self._build_aspect(merged_aspect)
            fields[aspect["name"]] = (
                aspect_model,
                Field(..., description=aspect.get("description", "")),
            )

        return create_model(dim["name"], **fields)

    def _build_schema(self):
        dimensions = self.instructions.get("dimensions", [])
        return [self._build_dimension(dim) for dim in dimensions]

    def _flatten_conv(self, conv_history: List[Dict]) -> str:
        """Convert conversation history to a string format."""
        lines = [
            f"{turn.get('role', 'unknown').capitalize()}: {turn.get('content', '')}"
            for turn in conv_history
        ]
        return "\n".join(lines)

    def _evaluate_dimensions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for dimension in self.dimensions:
            sys_prompt = self.instructions["sys_prompt"].render(
                data=data,
                granularity=self.configs.granularity,
                target=self.configs.target,
            )
            res = self.chat_model.generate(
                [{"role": "system", "content": sys_prompt}],
                response_format=dimension,
            )
            results[dimension.__name__] = res.model_dump()

        return results

    def evaluate(self, data: Any, *args) -> Dict[str, Any]:
        # Implement static evaluation logic here
        profile = data.get("profile", {})
        conv_history = data.get("messages", [])
        if not conv_history:
            return {}

        eval_data = {
            "profile": profile,
            "target": self.configs.target,
            "granularity": self.configs.granularity,
            "conv_history": conv_history,
            "last_response": "",
        }

        granularity = self.configs.granularity

        if granularity == "session":
            eval_data["conv_history"] = self._flatten_conv(conv_history)
            return self._evaluate_dimensions(eval_data)

        elif granularity == "turn":
            eval_data["conv_history"] = self._flatten_conv(conv_history[:-1])
            eval_data["last_response"] = conv_history[-1].get("content", "")
            return self._evaluate_dimensions(eval_data)

        elif granularity == "turn_by_turn":
            eval_data["granularity"] = "turn"
            results = {}
            for i, turn in enumerate(conv_history):
                if turn.get("role", "").lower() == self.configs.target.lower():
                    eval_data["conv_history"] = self._flatten_conv(conv_history[:i])
                    eval_data["last_response"] = turn.get("content", "")
                    res = self._evaluate_dimensions(eval_data)
                    results[f"turn_{i}"] = res
            return results

        raise ValueError(f"Unknown granularity: {granularity}")
