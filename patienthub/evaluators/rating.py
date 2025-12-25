from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field, create_model

from patienthub.base import EvaluatorAgent
from patienthub.configs import APIModelConfig
from patienthub.evaluators import Dimension, get_dimensions
from patienthub.utils import load_prompts, get_chat_model


@dataclass
class RatingEvaluatorConfig(APIModelConfig):
    """Configuration for Rating Evaluator."""

    target: str = "client"
    eval_type: str = "rating"
    dimensions: List[str] = field(default_factory=lambda: ["consistency"])
    granularity: str = "session"  # "turn" or "session"


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

    def generate(self, prompt, response_format: Type[BaseModel]) -> BaseModel:
        model = self.model.with_structured_output(response_format)
        return model.invoke([SystemMessage(content=prompt)])

    def evaluate_dimension(
        self, dimension: Dimension, profile=None, conv_history=None
    ) -> BaseModel:
        sys_prompt = self.prompts["sys_prompt"].render(
            data={"profile": profile, "conv_history": conv_history}
        )
        schema = self.dimension_schemas[dimension.name]
        res = self.generate(sys_prompt, response_format=schema)

        return res

    def evaluate_turn(self):
        target_role = self.configs.target
        profile = self.data.get("profile", {})
        conv_history = self.data.get("messages", [])

        results = {}
        for dimension in self.dimensions:
            results[dimension.name] = {}
            for i, msg in enumerate(conv_history):
                if msg.get("role") == target_role:
                    conv_history_slice = conv_history[: i + 1]
                    result = self.evaluate_turn(
                        dimension, profile=profile, conv_history=conv_history_slice
                    )
                    results[dimension.name][f"turn_{i}"] = result.model_dump()
        return results

    def evaluate_session(self):
        results = {}
        profile = self.data.get("profile", {})
        conv_history = self.data.get("messages", [])
        for dimension in self.dimensions:
            res = self.evaluate_dimension(
                dimension, profile=profile, conv_history=conv_history
            )
            results[dimension.name] = res.model_dump()
        return results

    def evaluate(self, data) -> Dict[str, Any]:

        self.data = data

        results = {}
        if self.configs.granularity == "session":
            results = self.evaluate_session()

        elif self.configs.granularity == "turn":
            results = self.evaluate_turn()

        results["data"] = data

        return results
