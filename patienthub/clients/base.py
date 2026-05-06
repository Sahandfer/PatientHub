import logging
from abc import ABC, abstractmethod
from omegaconf import DictConfig
from typing import Any, Dict, List
from patienthub.utils.models import get_chat_model
from patienthub.utils.files import load_json, load_prompts
from patienthub.schemas import get_profile_schema


logger = logging.getLogger(__name__)


class BaseClient(ABC):
    r"""Base class for all client agents."""

    def __init__(self, configs: DictConfig):
        r"""Initializes the client with the provided configurations."""
        self.configs = configs
        self.data = self.load_data()
        self.prompts = self.load_prompts()
        self.chat_model = self.load_chat_model()
        self.therapist = None

        self.build_sys_prompt()

    def set_therapist(
        self,
        therapist: Any,
        prev_sessions: List[Dict[str, str]] | None = None,
    ) -> None:
        r"""Sets the therapist information for the client."""
        self.therapist = getattr(therapist, "name", None) or "Therapist"

    def load_data(self) -> Dict[str, Any] | None:
        r"""Loads and validates the client's character data using the registered schema."""
        if hasattr(self.configs, "data_path"):
            try:
                data = load_json(self.configs.data_path)[self.configs.data_idx]
                get_profile_schema(self.configs.agent_name).model_validate(data)
            except Exception as e:
                raise ValueError(
                    f"Error loading or validating data for client '{self.configs.agent_name}: {e}'"
                )
            return data
        return None

    def load_prompts(self) -> Dict[str, Any] | None:
        if hasattr(self.configs, "prompt_path"):
            return load_prompts(path=self.configs.prompt_path, lang=self.configs.lang)
        return None

    def load_chat_model(self) -> Any | None:
        if hasattr(self.configs, "model_type") and hasattr(self.configs, "model_name"):
            return get_chat_model(self.configs)
        return None

    def reset(self) -> None:
        r"""Resets the client to its initial state."""
        self.build_sys_prompt()
        self.therapist = None

    @abstractmethod
    def build_sys_prompt(self) -> None:
        r"""Builds the system prompt based on the client's profile and other relevant information."""
        pass

    @abstractmethod
    def generate_response(self, msg: str) -> str:
        r"""Generates a response based on the input message."""
        pass
