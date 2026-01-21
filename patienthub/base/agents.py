from abc import ABC, abstractmethod
from pydantic import BaseModel
from omegaconf import DictConfig
from typing import Any, Dict, List, Type, Optional


class TrainableAgent(ABC):
    r"""An abstract base class for trainable agents."""

    @abstractmethod
    def train(self, data: List[Dict[str, Any]], *args: Any, **kwargs: Any) -> None:
        r"""Trains the agent using the provided data."""
        pass

    @abstractmethod
    def evaluate(
        self, data: List[Dict[str, Any]], *args: Any, **kwargs: Any
    ) -> Dict[str, float]:
        r"""Evaluates the agent's performance on the provided data."""
        pass


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


class ChatAgent(ABC):
    r"""An abstract base class for chat agents."""

    chat_model: Any
    data: Dict[str, Any]
    messages: List[str] | List[Dict[str, Any]]
    lang: str

    @abstractmethod
    def reset(self, *args: Any) -> None:
        r"""Resets the ChatAgent to its initial state."""
        pass


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
