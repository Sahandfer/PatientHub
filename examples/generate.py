"""
An example for generating characters for simulations.
It requires:
    - A generator agent (specified by generator in the configuration)
It creates and saves a character based on the specified configurations.

Usage:
    # Generate with defaults
    uv run python -m examples.generate

    # Override generator type
    uv run python -m examples.generate generator=psyche

    # Enable verbose logging (DEBUG level)
    uv run python -m examples.generate verbose=true

Logs are saved to logs/generate_<timestamp>.log.
"""

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.generators import get_generator
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class GenerateConfig:
    """Configuration for generating data."""

    generator: str = "annaAgent"
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="generate", node=GenerateConfig)


@hydra.main(version_base=None, config_name="generate")
def generate(configs: DictConfig):
    init_logging(
        "generate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )
    logger.info(
        "Starting generation: generator=%s, lang=%s", configs.generator, configs.lang
    )
    try:
        generator = get_generator(agent_name=configs.generator, lang=configs.lang)
        generator.generate_character()
    except KeyboardInterrupt:
        logger.warning("Generation interrupted by user.")


if __name__ == "__main__":
    generate()
