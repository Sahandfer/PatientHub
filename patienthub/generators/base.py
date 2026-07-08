# coding=utf-8
# Licensed under the MIT License;

from abc import ABC, abstractmethod
from typing import Any
from omegaconf import DictConfig

from patienthub.schemas import get_seed_schema
from patienthub.utils import load_prompts, resolve_path, get_chat_model


class BaseGenerator(ABC):
    """Base class for character generators."""

    def __init__(self, configs: DictConfig):
        r"""Initialize the generator (chat model, prompts, and static resources)."""
        self.configs = configs
        self.chat_model = self.load_chat_model()
        self.prompts = self.load_prompts()

    def prepare_seed(self, data: dict[str, Any] | None) -> dict[str, Any] | None:
        if data is None:
            return None
        schema = get_seed_schema(getattr(self.configs, "agent_name", None))
        if schema is None:
            return data
        return schema.model_validate(data).model_dump()

    def load_chat_model(self) -> Any | None:
        if hasattr(self.configs, "model_type") and hasattr(self.configs, "model_name"):
            return get_chat_model(self.configs)
        return None

    def load_prompts(self) -> dict[str, Any] | None:
        if hasattr(self.configs, "prompt_path"):
            path = resolve_path(self.configs.prompt_path)
            return load_prompts(path=path, lang=self.configs.lang)
        return None

    @abstractmethod
    def generate_character(self, data: dict[str, Any] | None = None) -> Any:
        r"""Build one character and return it."""
        raise NotImplementedError
