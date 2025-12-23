from .agent_files import AgentFilesGenerator, AgentFilesGeneratorConfig
from .student import StudentClientGenerator, StudentClientGeneratorConfig
from .psyche import PsycheGenerator, PsycheGeneratorConfig
from .clientCast import ClientCastGenerator, ClientCastGeneratorConfig

from omegaconf import DictConfig

# Registry of generator implementations
GENERATORS = {
    "agent_files": AgentFilesGenerator,
    "student": StudentClientGenerator,
    "psyche": PsycheGenerator,
    "clientCast": ClientCastGenerator,
}

# Registry of generator configs (for Hydra registration)
GENERATOR_CONFIG_REGISTRY = {
    "agent_files": AgentFilesGeneratorConfig,
    "student": StudentClientGeneratorConfig,
    "psyche": PsycheGeneratorConfig,
    "clientCast": ClientCastGeneratorConfig,
}


def get_generator(configs: DictConfig):
    agent_type = configs.generator.agent_type
    print(f"Loading {agent_type} generator...")
    if agent_type in GENERATORS:
        return GENERATORS[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown generator type: {agent_type}")


def register_generator_configs(cs):
    for name, config_cls in GENERATOR_CONFIG_REGISTRY.items():
        cs.store(group="generator", name=name, node=config_cls)


__all__ = [
    "get_generator",
    "register_generator_configs",
]
