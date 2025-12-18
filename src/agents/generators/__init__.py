from .student import StudentClientGenerator
from .psyche import PsycheGenerator

from omegaconf import DictConfig

GENERATORS = {
    "student": StudentClientGenerator,
    "psyche": PsycheGenerator,
}


def get_generator(configs: DictConfig):
    agent_type = configs.generator.agent_type
    print(f"Loading {agent_type} generator...")
    if agent_type in GENERATORS:
        return GENERATORS[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown generator type: {agent_type}")


__all__ = ["StudentClientGenerator", "PsycheGenerator"]
