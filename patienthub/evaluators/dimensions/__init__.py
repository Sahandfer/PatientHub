from .base import Dimension, Aspect
from .consistency import CONSISTENCY

from omegaconf import DictConfig

DIMENSION_REGISTRY = {"consistency": CONSISTENCY}


def get_dimensions(dimensions):
    return [DIMENSION_REGISTRY[name] for name in dimensions]


__all__ = ["Dimension", "Aspect", "get_dimensions"]
