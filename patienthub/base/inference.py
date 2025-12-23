from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict, Type, Optional


class InferenceAgent(ABC):
    r"""An abstract base class for inference agents."""

    chat_model: Any
    data: Dict[str, Any]
    lang: str

    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
    ) -> BaseModel | str:
        r"""Generates a response based on the input prompt."""
        pass
