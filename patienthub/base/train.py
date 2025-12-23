from abc import ABC, abstractmethod
from typing import Any, Dict, List


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
