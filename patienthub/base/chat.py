from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict, List, Type, Optional


class ChatAgent(ABC):
    r"""An abstract base class for chat agents."""

    chat_model: Any
    data: Dict[str, Any]
    messages: List[str] | List[Dict[str, Any]]
    lang: str

    @abstractmethod
    def generate(
        self,
        messages: List[str] | List[Dict[str, Any]] = [],
        response_format: Optional[Type[BaseModel]] = None,
    ) -> BaseModel | str:
        r"""Generates a response based on the input messages."""
        pass

    @abstractmethod
    def reset(self, *args: Any) -> None:
        r"""Resets the ChatAgent to its initial state."""
        pass
