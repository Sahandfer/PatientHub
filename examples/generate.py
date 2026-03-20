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
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.generators import get_generator


@dataclass
class GenerateConfig:
    """Configuration for generating data."""

    generator: str = "annaAgent"
    lang: str = "en"


cs = ConfigStore.instance()
cs.store(name="generate", node=GenerateConfig)


@hydra.main(version_base=None, config_name="generate")
def generate(configs: DictConfig):
    generator = get_generator(agent_name=configs.generator, lang=configs.lang)
    generator.generate_character()


if __name__ == "__main__":
    generate()
