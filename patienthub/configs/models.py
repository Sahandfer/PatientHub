from dataclasses import dataclass


@dataclass
class APIModelConfig:
    """Base configuration shared by all agents using API models."""

    agent_type: str = ""
    model_type: str = "LAB"
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 8192
    max_retries: int = 3
    lang: str = "en"


@dataclass
class LocalModelConfig:
    """Base configuration for locally-hosted models."""

    agent_type: str = ""
    model_type: str = "local"
    model_name: str = ""
    temperature: float = 0.3
    max_tokens: int = 8192
    max_new_tokens: int = 128
    repetition_penalty: float = 1.2
    device: int = 0
    lang: str = "en"
