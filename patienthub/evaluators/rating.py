from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field, create_model
from langchain_core.messages import SystemMessage, HumanMessage

from patienthub.evaluators.dimensions import Dimension, get_dimensions
from patienthub.base import InferenceAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class RatingEvaluatorConfig(APIModelConfig):
    """Configuration for Rating Evaluator."""

    target: str = "client"
    eval_type: str = "rating"
    dimensions: List[str] = field(default_factory=lambda: ["consistency"])
    granularity: str = "session"  # "turn" or "session"


class RatingEvaluator(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="evaluator", agent_type="rating", lang=configs.lang
        )
        self.dimensions = get_dimensions(configs.dimensions)
        self.dimension_schemas = {
            dimension.name: self.build_schema(dimension)
            for dimension in self.dimensions
        }

    def build_schema(self, dimension: Dimension) -> Type[BaseModel]:
        """Dynamically create a Pydantic model for rating a dimension."""
        AspectRating = create_model(
            "AspectRating",
            score=(int, Field(..., ge=1, le=10, description="Score from 1-10")),
            comments=(str, Field(..., description="Reasoning for the score")),
        )

        fields = {
            aspect.name: (AspectRating, Field(..., description=aspect.description))
            for aspect in dimension.aspects
        }

        fields["overall_score"] = (
            int,
            Field(..., ge=1, le=10, description="Overall score for this dimension"),
        )

        return create_model(f"{dimension.name.title()}Rating", **fields)

    def build_dimension_prompt(self, dimension: Dimension) -> str:
        """Build prompt section describing what to evaluate for a dimension."""
        lines = [f"## {dimension.name.title()}", f"{dimension.description}", ""]
        lines.append("Evaluate the following aspects:")
        for aspect in dimension.aspects:
            lines.append(f"- **{aspect.name}**: {aspect.description}")
            if aspect.guidelines:
                lines.append(f"  - Guidelines: {aspect.guidelines}")
        return "\n".join(lines)

    def generate(
        self,
        prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
    ) -> BaseModel | str:
        """Generate a response from the chat model."""
        if response_format:
            chat_model = self.chat_model.with_structured_output(response_format)
        else:
            chat_model = self.chat_model
        return chat_model.invoke(prompt)

    def evaluate_dimension(self, dimension: Dimension) -> BaseModel:
        """Evaluate a single dimension."""
        schema = self.dimension_schemas[dimension.name]

        # Build the system prompt with context
        sys_prompt = self.prompts["sys_prompt"].render(
            data={
                "profile": self.data.get("profile"),
                "conv_history": self.data.get("messages", []),
            }
        )

        # Build the dimension-specific instructions
        dimension_prompt = self.build_dimension_prompt(dimension)

        full_prompt = [
            SystemMessage(content=sys_prompt),
            HumanMessage(
                content=f"Please evaluate the following dimension:\n\n{dimension_prompt}"
            ),
        ]

        res = self.generate(full_prompt, response_format=schema)

        return res

    def evaluate_turn(self, dimension: Dimension, turn_idx: int) -> BaseModel:
        """Evaluate a single turn for a dimension."""
        schema = self.dimension_schemas[dimension.name]
        messages = self.data.get("messages", [])

        # Get conversation up to and including the target turn
        context_messages = messages[:turn_idx]
        target_message = messages[turn_idx]

        sys_prompt = self.prompts["sys_prompt"].render(
            data={
                "profile": self.data.get("profile"),
                "conv_history": (
                    self.data.get("messages", []) if context_messages else None
                ),
            }
        )

        dimension_prompt = self.build_dimension_prompt(dimension)

        full_prompt = [
            SystemMessage(content=sys_prompt),
            HumanMessage(
                content=(
                    f"Please evaluate the following response:\n\n"
                    f"**{target_message['role']}**: {target_message['content']}\n\n"
                    f"Evaluate based on this dimension:\n\n{dimension_prompt}"
                )
            ),
        ]

        chat_model = self.chat_model.with_structured_output(schema)
        return chat_model.invoke(full_prompt)

    def evaluate(self, data) -> Dict[str, Any]:
        """
        Evaluate conversation data across all dimensions.

        Args:
            data: Dictionary containing 'profile' and 'messages'

        Returns:
            Dictionary with evaluation results per dimension
        """
        self.data = data
        results = {}

        if self.configs.granularity == "session":
            # Evaluate entire session
            for dimension in self.dimensions:
                result = self.evaluate_dimension(dimension)
                results[dimension.name] = result.model_dump()

        elif self.configs.granularity == "turn":
            # Evaluate each turn separately
            messages = self.data.get("messages", [])
            target_role = "Client" if self.configs.target == "client" else "Therapist"

            for dimension in self.dimensions:
                results[dimension.name] = {}
                for i, msg in enumerate(messages):
                    if msg.get("role") == target_role:
                        result = self.evaluate_turn(dimension, i)
                        results[dimension.name][f"turn_{i}"] = result.model_dump()

        return results
