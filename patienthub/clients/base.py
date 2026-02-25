from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseClient(ABC):
    r"""Base class for all client agents."""

    name: str
    chat_model: Any
    configs: Dict[str, Any]
    messages: List[str] | List[Dict[str, Any]]
    lang: str

    def set_therapist(
        self,
        therapist: Dict[str, Any],
        prev_sessions: List[Dict[str, str]] | None = None,
    ) -> None:
        r"""Sets the therapist information for the client."""
        self.therapist = therapist.get("name", "Therapist")

    @abstractmethod
    def build_sys_prompt(self) -> None:
        r"""Builds the system prompt based on the client's profile and other relevant information."""
        pass

    @abstractmethod
    def generate_response(self, msg: str) -> str:
        r"""Generates a response based on the input message."""
        pass

    @abstractmethod
    def reset(self) -> None:
        r"""Resets the client to its initial state."""
        pass
