"""
Generate a patient character profile.

Usage:
    # Generate with defaults (annaAgent)
    patienthub generate

    # Pick a generator
    patienthub generate generator=deprofile

    # Override generator config fields
    patienthub generate generator=deprofile \
        generator.profile_id=0069 generator.temperature=0

    # Language and verbose logging
    patienthub generate generator=deprofile lang=zh verbose=true

Logs are saved to logs/generate_<timestamp>.log.
"""

from dataclasses import dataclass, field
from typing import Any, List

import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStore

from patienthub.generators import get_generator, register_generator_configs
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class GenerateConfig:
    """Configuration for generating data."""

    defaults: List[Any] = field(
        default_factory=lambda: ["_self_", {"generator": "annaAgent"}]
    )
    generator: Any = MISSING
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="generate", node=GenerateConfig)
register_generator_configs(cs)


@hydra.main(version_base=None, config_name="generate")
def generate(configs: DictConfig):
    init_logging(
        "generate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )
    generator_config = configs.generator
    agent_name = generator_config.agent_name
    logger.info("Starting generation: generator=%s, lang=%s", agent_name, configs.lang)
    try:
        generator = get_generator(
            agent_name=agent_name, configs=generator_config, lang=configs.lang
        )
        generator.generate_character()
    except KeyboardInterrupt:
        logger.warning("Generation interrupted by user.")


if __name__ == "__main__":
    generate()
