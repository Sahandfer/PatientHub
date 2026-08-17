# coding=utf-8
# Licensed under the MIT License;

from .base import BaseGenerator
from .psyche import PsycheGenerator, PsycheGeneratorConfig
from .clientCast import ClientCastGenerator, ClientCastGeneratorConfig
from .annaAgent import AnnaAgentGenerator, AnnaAgentGeneratorConfig
from .patientZero import PatientZeroGenerator, PatientZeroGeneratorConfig
from .deprofile import DeprofileGenerator, DeprofileGeneratorConfig
from .patientAct import PatientActGenerator, PatientActGeneratorConfig
from .cars import CarsGenerator, CarsGeneratorConfig


from omegaconf import DictConfig

from patienthub.utils.logger import get_logger, language_warning

logger = get_logger(__name__)

# Registry of generator implementations
GENERATORS = {
    "psyche": PsycheGenerator,
    "clientCast": ClientCastGenerator,
    "annaAgent": AnnaAgentGenerator,
    "patientZero": PatientZeroGenerator,
    "deprofile": DeprofileGenerator,
    "cars": CarsGenerator,
    "patientAct": PatientActGenerator,
}

GENERATOR_DEFAULT_LANGS = {
    "annaAgent": "en",
    "patientZero": "en",
    "deprofile": "zh",
    "psyche": "en",
    "clientCast": "en",
    "cars": "en",
    "patientAct": "en",
}

# Registry of generator configs (for Hydra registration)
GENERATOR_CONFIG_REGISTRY = {
    "psyche": PsycheGeneratorConfig,
    "clientCast": ClientCastGeneratorConfig,
    "annaAgent": AnnaAgentGeneratorConfig,
    "patientZero": PatientZeroGeneratorConfig,
    "deprofile": DeprofileGeneratorConfig,
    "cars": CarsGeneratorConfig,
    "patientAct": PatientActGeneratorConfig,
}


def get_generator(agent_name: str, configs: DictConfig = None, lang: str = "en"):
    logger.info("Loading %s generator...", agent_name)
    if agent_name in GENERATORS:
        if configs is None:
            configs = get_generator_config(agent_name)
        configs.lang = lang
        language_warning(
            agent_name, configs.lang, GENERATOR_DEFAULT_LANGS.get(agent_name, None)
        )
        return GENERATORS[agent_name](configs=configs)
    else:
        raise ValueError(f"Unknown generator type: {agent_name}")


def get_generator_config(agent_name: str):
    if agent_name in GENERATOR_CONFIG_REGISTRY:
        return GENERATOR_CONFIG_REGISTRY[agent_name]()
    else:
        raise ValueError(f"Generator config for {agent_name} not found in registry.")


def register_generator_configs(cs):
    for name, config_cls in GENERATOR_CONFIG_REGISTRY.items():
        cs.store(group="generator", name=name, node=config_cls)


__all__ = [
    "BaseGenerator",
    "get_generator",
    "get_generator_config",
    "register_generator_configs",
]
