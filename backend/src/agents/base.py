from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    r"""An abstract base class for all agents."""

    role: str
    agent_type: str
    model_client: Any
    data: Dict[str, Any]
    messages: List[Any]

    @abstractmethod
    def generate(self, messages: List[str], response_format: Any) -> Any:
        r"""Processes the input messages and returns a response."""
        pass

    @abstractmethod
    def reset(self, *args: Any, **kwargs: Any) -> Any:
        r"""Resets the agent to its initial state."""
        pass
