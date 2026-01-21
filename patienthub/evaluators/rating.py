from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type
from pydantic import BaseModel, Field, create_model

from .dimensions import Dimension, get_dimensions
from patienthub.base import EvaluatorAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model


@dataclass
class RatingEvaluatorConfig(APIModelConfig):
    """Configuration for Rating Evaluator."""

    target: str = "client"
    eval_type: str = "rating"
    dimensions: List[str] = field(default_factory=lambda: ["consistency"])
    granularity: str = "session"  # "turn", "turn_by_turn" or "session"


@dataclass
class AspectRating(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score for this aspect")
    comments: str = Field(..., description="Reasoning for the score (1 sentence)")


class RatingEvaluator(EvaluatorAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="evaluator", agent_type="rating", lang=configs.lang
        )
        self.dimensions = get_dimensions(configs.dimensions)
        self.dimension_schemas = {
            dimension.name: self.build_schema(dimension)
            for dimension in self.dimensions
        }

        self.target = configs.target.lower()
        self.granularity = configs.granularity

    def build_schema(self, dimension: Dimension) -> Type[BaseModel]:
        """
        Create a Pydantic BaseModel class for rating a dimension.
        Field descriptions come from aspect descriptions.
        """
        fields = {
            aspect.name: (AspectRating, Field(..., description=aspect.description))
            for aspect in dimension.aspects
        }

        fields["overall_score"] = (
            int,
            Field(..., ge=0, le=10, description="Overall score for this dimension"),
        )

        return create_model(f"{dimension.name.title()}Rating", **fields)

    def flatten_conv(self, conv_history: List[Dict]) -> str:
        return "\n".join(
            [f"{msg['role'].lower()}: {msg['content']}" for msg in conv_history]
        )

    def evaluate_dimensions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for dimension in self.dimensions:
            schema = self.dimension_schemas[dimension.name]
            sys_prompt = self.prompts["sys_prompt"].render(data=data)
            res = self.chat_model.generate(
                {"role": "system", "content": sys_prompt}, response_format=schema
            )
            results[dimension.name] = res.model_dump()

        return results

    def evaluate(self, data) -> Dict[str, Any]:
        profile = data.get("profile", {})
        conv_history = data.get("messages", [])
        if len(conv_history) == 0:
            return {}

        granularity = self.configs.granularity
        data = {
            "profile": profile,
            "target": self.target,
            "granularity": granularity,
            "conv_history": conv_history,
            "last_response": "",
        }
        results = {}
        if granularity == "session":
            data["conv_history"] = self.flatten_conv(conv_history)
            results = self.evaluate_dimensions(data)
        elif granularity == "turn":
            data["conv_history"] = self.flatten_conv(conv_history[:-1])
            data["last_response"] = conv_history[-1]["content"]
            results = self.evaluate_dimensions(data)
        elif granularity == "turn_by_turn":
            data["granularity"] = "turn"
            for i, turn in enumerate(conv_history):
                role = turn.get("role").lower()

                if role == self.target:
                    data["conv_history"] = self.flatten_conv(conv_history[:i])
                    data["last_response"] = turn.get("content", "")
                    res = self.evaluate_dimensions(data)
                    results[f"turn_{i}"] = res

        return results
