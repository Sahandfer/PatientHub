"""
An example for generating characters for simulations.
It requires:
    - A generator agent (specified by gen_type in the configuration)
It creates and saves a character based on the specified configurations.

Usage:
    # Generate with defaults
    uv run python -m examples.generate

    # Override generator type
    uv run python -m examples.generate generator=psyche
"""

import hydra
from typing import Any, List
from dataclasses import dataclass, field
from omegaconf import DictConfig, MISSING

from patienthub.configs import register_configs
from patienthub.generators import get_generator

DEFAULTS = [
    "_self_",
    {"generator": "clientCast"},
]


@dataclass
class GenerateConfig:
    """Configuration for generating data."""

    defaults: List[Any] = field(default_factory=lambda: DEFAULTS)
    generator: Any = MISSING
    gen_type: str = "client"
    lang: str = "en"


register_configs("generate", GenerateConfig)


def generate_client(configs: DictConfig):
    generator = get_generator(configs=configs)
    generator.generate_character()


@hydra.main(version_base=None, config_name="generate")
def generate(configs: DictConfig):
    if configs.gen_type == "client":
        generate_client(configs)
    else:
        print("Generation type is not supported.")


if __name__ == "__main__":
    generate()
