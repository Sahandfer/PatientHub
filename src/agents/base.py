from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    r"""An abstract base class for all agents."""

    role: str
    agent_type: str


class TrainableAgent(BaseAgent):
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


class InferenceAgent(BaseAgent):
    r"""An abstract base class for inference agents."""

    model_client: Any
    data: Dict[str, Any]
    messages: List[Any]
    lang: str

    @abstractmethod
    def generate(self, messages: List[str], response_format: Any) -> Any:
        r"""Processes the input messages and returns a response."""
        pass

    @abstractmethod
    def reset(self, *args: Any, **kwargs: Any) -> Any:
        r"""Resets the agent to its initial state."""
        pass


class UserAgent(BaseAgent):
    r"""An abstract base class for users as agents."""

    messages: List[Any]
    lang: str

    @abstractmethod
    def generate(self, response_format: Any) -> Any:
        r"""Processes the user input and returns a response."""
        pass

    @abstractmethod
    def reset(self, *args: Any, **kwargs: Any) -> Any:
        r"""Resets the user agent to its initial state."""
        pass
