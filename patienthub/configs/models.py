from dataclasses import dataclass


@dataclass
class APIModelConfig:
    """Base configuration shared by all agents using API models."""

    model_type: str = "OPENAI"
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 8192
    max_retries: int = 3
    lang: str = "en"


@dataclass
class LocalModelConfig:
    """Base configuration for local models."""

    model_type: str = "LOCAL"
    model_name: str = ""
    temperature: float = 0.3
    max_tokens: int = 8192
    max_new_tokens: int = 128
    repetition_penalty: float = 1.2
    device: int = 0
    lang: str = "en"
