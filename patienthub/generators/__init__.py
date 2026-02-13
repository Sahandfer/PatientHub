from .base import BaseGenerator
from .psyche import PsycheGenerator, PsycheGeneratorConfig
from .clientCast import ClientCastGenerator, ClientCastGeneratorConfig
from .annaAgent import AnnaAgentGenerator, AnnaAgentGeneratorConfig


from omegaconf import DictConfig

# Registry of generator implementations
GENERATORS = {
    "psyche": PsycheGenerator,
    "clientCast": ClientCastGenerator,
    "annaAgent": AnnaAgentGenerator,
}

# Registry of generator configs (for Hydra registration)
GENERATOR_CONFIG_REGISTRY = {
    "psyche": PsycheGeneratorConfig,
    "clientCast": ClientCastGeneratorConfig,
    "annaAgent": AnnaAgentGeneratorConfig,
}


def get_generator(configs: DictConfig, lang: str = "en"):
    if hasattr(configs, "lang"):
        configs.lang = lang
    agent_type = configs.agent_type
    print(f"Loading {agent_type} generator...")
    if agent_type in GENERATORS:
        return GENERATORS[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown generator type: {agent_type}")


def register_generator_configs(cs):
    for name, config_cls in GENERATOR_CONFIG_REGISTRY.items():
        cs.store(group="generator", name=name, node=config_cls)


__all__ = [
    "BaseGenerator",
    "get_generator",
    "register_generator_configs",
]
