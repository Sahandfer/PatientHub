from .base import BaseAgent, InferenceAgent, TrainableAgent, UserAgent

from .clients import get_client
from .evaluators import get_evaluator
from .therapists import get_therapist

from omegaconf import DictConfig


def get_inference_agent(category: str, configs: DictConfig):
    if category == "client":
        return get_client(configs=configs)
    elif category == "evaluator":
        return get_evaluator(configs=configs)
    elif category == "therapist":
        return get_therapist(configs=configs)
    else:
        raise ValueError(f"Unknown agent category: {category}")


__all__ = [
    "BaseAgent",
    "InferenceAgent",
    "TrainableAgent",
    "UserAgent",
    "get_inference_agent",
]
