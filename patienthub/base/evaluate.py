from abc import ABC, abstractmethod
from pydantic import BaseModel
from omegaconf import DictConfig
from typing import Any, Type, Optional


class EvaluatorAgent(ABC):
    r"""An abstract base class for chat agents."""

    configs: DictConfig
    model: Any
    lang: str

    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
    ) -> BaseModel | str:
        r"""Generates a evaluation based on the input messages."""
        pass

    @abstractmethod
    def evaluate(self, data: Any, *args) -> None:
        r"""Evaluates the data using the EvaluatorAgent."""
        pass
