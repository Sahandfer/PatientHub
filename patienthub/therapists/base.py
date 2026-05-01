from abc import ABC, abstractmethod
from typing import Any, Dict, List
from omegaconf import DictConfig
from patienthub.utils.models import get_chat_model
from patienthub.utils.files import load_prompts


class BaseTherapist(ABC):
    r"""Base class for all therapist agents."""

    def __init__(self, configs: DictConfig):
        r"""Initializes the therapist with the provided configurations."""
        self.configs = configs
        self.chat_model = self.load_chat_model()
        self.prompts = self.load_prompts()
        self.client = None

        self.build_sys_prompt()

    def set_client(
        self,
        client: Any,
        prev_sessions: List[Dict[str, str]] | None = None,
    ) -> None:
        r"""Sets the client information for the therapist."""
        self.client = getattr(client, "name", None) or "Client"

    def load_prompts(self) -> Dict[str, Any] | None:
        if hasattr(self.configs, "prompt_path"):
            return load_prompts(path=self.configs.prompt_path, lang=self.configs.lang)
        return None

    def load_chat_model(self) -> Any | None:
        if hasattr(self.configs, "model_type") and hasattr(self.configs, "model_name"):
            return get_chat_model(self.configs)
        return None

    def reset(self) -> None:
        r"""Resets the therapist to its initial state."""
        self.build_sys_prompt()
        self.client = None

    @abstractmethod
    def build_sys_prompt(self) -> None:
        r"""Builds the system prompt based on the client's profile and other relevant information."""
        pass

    @abstractmethod
    def generate_response(self, msg: str) -> str:
        r"""Generates a response based on the input message."""
        pass
