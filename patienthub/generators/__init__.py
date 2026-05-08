from .base import BaseGenerator
from .psyche import PsycheGenerator, PsycheGeneratorConfig
from .clientCast import ClientCastGenerator, ClientCastGeneratorConfig
from .annaAgent import AnnaAgentGenerator, AnnaAgentGeneratorConfig
from .patientZero import PatientZeroGenerator, PatientZeroGeneratorConfig


from omegaconf import DictConfig

# Registry of generator implementations
GENERATORS = {
    "psyche": PsycheGenerator,
    "clientCast": ClientCastGenerator,
    "annaAgent": AnnaAgentGenerator,
    "patientZero": PatientZeroGenerator,
}

# Registry of generator configs (for Hydra registration)
GENERATOR_CONFIG_REGISTRY = {
    "psyche": PsycheGeneratorConfig,
    "clientCast": ClientCastGeneratorConfig,
    "annaAgent": AnnaAgentGeneratorConfig,
    "patientZero": PatientZeroGeneratorConfig,
}


def get_generator(agent_name: str, configs: DictConfig = None, lang: str = "en"):
    print(f"Loading {agent_name} generator...")
    if agent_name in GENERATORS:
        if configs is None:
            configs = get_generator_config(agent_name)
        configs.lang = lang
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
        cs.store(group="generator_configs", name=name, node=config_cls)


__all__ = [
    "BaseGenerator",
    "get_generator",
    "get_generator_config",
    "register_generator_configs",
]
