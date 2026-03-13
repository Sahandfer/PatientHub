from abc import ABC
from jinja2 import Template
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import Field, create_model
from typing import Any, Dict, List, Literal

from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model

PARADIGMS = {"binary", "scalar", "categorical", "extraction"}


@dataclass
class LLMJudgeConfig(APIModelConfig):
    prompt_path: str = ""
    use_reasoning: bool = False


class LLMJudge(ABC):
    """Evaluates conversations using an LLM as a judge."""

    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(configs)

        try:
            self.instructions = load_prompts(
                path=configs.prompt_path, lang=self.configs.lang, process=False
            )
            self.dimensions = self.build_schema()
        except Exception as e:
            print(f"Error loading prompts or building schema: {e}")
            raise e

    def build_binary_field(self, data: Dict) -> Dict[str, Any]:
        name, ftype = "label", bool
        kwargs = {"description": data.get("description", "True if aspect is present")}
        return {name: (ftype, Field(..., **kwargs))}

    def build_scalar_field(self, data: Dict) -> Dict[str, Any]:
        name, ftype = "score", int
        min_val, max_val = data.get("range", [1, 5])
        kwargs = {
            "ge": min_val,
            "le": max_val,
            "description": data.get("description", "Rating for this aspect"),
        }
        return {name: (ftype, Field(..., **kwargs))}

    def build_categorical_field(self, data: Dict) -> Dict[str, Any]:
        labels = tuple(data.get("labels", ["good", "average", "bad"]))
        name, ftype = "label", Literal[labels]
        kwargs = {"description": data.get("description", "Assigned label")}
        return {name: (ftype, Field(..., **kwargs))}

    def build_extraction_field(self, data: Dict) -> Dict[str, Any]:
        name, ftype = "snippets", List[str]
        kwargs = {"description": data.get("description", "Relevant Snippets")}
        return {name: (ftype, Field(..., **kwargs))}

    def build_field(self, data: Dict) -> Dict[str, Any]:
        paradigm = data.get("paradigm", "")
        if paradigm not in PARADIGMS:
            print(
                f"Unsupported paradigm: {paradigm}. Must be one of {PARADIGMS}. Skipping \"{data.get('name', 'unknown')}\"."
            )
            return {}

        field_builder = getattr(self, f"build_{paradigm}_field")
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

    def build_aspect(self, aspect: Dict) -> Any:
        fields = self.build_field(data=aspect)
        return create_model(aspect["name"], **fields)

    def build_dimension(self, dim: Dict):
        fields = {}
        aspects = dim.get("aspects", [])
        if not aspects:
            fields = self.build_field(data=dim)
            return create_model(dim["name"], **fields)

        inherit_keys = {
            k: v for k, v in dim.items() if k not in {"name", "description", "aspects"}
        }

        fields = {}
        for aspect in aspects:
            # Inherit keys from dimension (e.g., range, labels)
            merged_aspect = {**inherit_keys, **aspect}
            aspect_model = self.build_aspect(merged_aspect)
            fields[aspect["name"]] = (
                aspect_model,
                Field(..., description=aspect.get("description", "")),
            )

        return create_model(dim["name"], **fields)

    def build_schema(self):
        dimensions = self.instructions.get("dimensions", [])
        return [self.build_dimension(dim) for dim in dimensions]

    def evaluate_dimension(self, dim: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        sys_prompt = Template(self.instructions["sys_prompt"]).render(data=data)
        res = self.chat_model.generate(
            [{"role": "system", "content": sys_prompt}],
            response_format=dim,
        )
        return res.model_dump()

    def evaluate_dimensions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}

        for dimension in self.dimensions:
            res = self.evaluate_dimension(dimension, data)
            results[dimension.__name__] = res

        return results
