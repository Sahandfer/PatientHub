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
    def create_agent(self, *args: Any, **kwargs: Any) -> Any:
        r"""Performs a single step of the agent."""
        pass

    @abstractmethod
    def reset(self, *args: Any, **kwargs: Any) -> Any:
        r"""Resets the agent to its initial state."""
        pass
