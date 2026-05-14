from abc import ABC, abstractmethod
from typing import Any, Dict
from omegaconf import DictConfig

from patienthub.utils import load_prompts, resolve_path, get_chat_model


class BaseGenerator(ABC):
    def __init__(self, configs: DictConfig):
        r"""Initializes the generator with the provided configurations."""
        self.configs = configs
        self.chat_model = self.load_chat_model()
        self.prompts = self.load_prompts()

    def load_chat_model(self) -> Any | None:
        if hasattr(self.configs, "model_type") and hasattr(self.configs, "model_name"):
            return get_chat_model(self.configs)
        return None

    def load_prompts(self) -> Dict[str, Any] | None:
        if hasattr(self.configs, "prompt_path"):
            path = resolve_path(self.configs.prompt_path)
            return load_prompts(path=path, lang=self.configs.lang)
        return None

    @abstractmethod
    def generate_character(self) -> Dict[str, Any]:
        r"""Generates a character profile based on the provided configurations."""
        pass
