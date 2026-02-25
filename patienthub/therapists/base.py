from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseTherapist(ABC):
    r"""Base class for all therapist agents."""

    name: str
    chat_model: Any
    configs: Dict[str, Any]
    messages: List[str] | List[Dict[str, Any]]
    lang: str

    def set_client(
        self,
        client: Dict[str, Any],
        prev_sessions: List[Dict[str, str]] | None = None,
    ) -> None:
        r"""Sets the client information for the therapist."""
        self.client = client.get("name", "Client")

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
        r"""Resets the therapist to its initial state."""
        pass
