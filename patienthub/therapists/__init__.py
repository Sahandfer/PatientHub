from .base import BaseTherapist
from .basic import BasicTherapist, BasicTherapistConfig
from .eliza import ElizaTherapist, ElizaTherapistConfig
from .user import UserTherapist, UserTherapistConfig
from .psyche import PsycheTherapist, PsycheTherapistConfig
from .cami import CamiTherapist, CamiTherapistConfig


from omegaconf import DictConfig

# Registry of therapist implementations
THERAPIST_REGISTRY = {
    "basic": BasicTherapist,
    "eliza": ElizaTherapist,
    "user": UserTherapist,
    "psyche": PsycheTherapist,
    "cami": CamiTherapist,
}

# Registry of therapist configs (for Hydra registration)
THERAPIST_CONFIG_REGISTRY = {
    "basic": BasicTherapistConfig,
    "eliza": ElizaTherapistConfig,
    "user": UserTherapistConfig,
    "psyche": PsycheTherapistConfig,
    "cami": CamiTherapistConfig,
}


def get_therapist(configs: DictConfig, lang: str = "en"):
    configs.lang = lang
    agent_type = configs.agent_type
    print(f"Loading {agent_type} therapist agent...")
    if agent_type in THERAPIST_REGISTRY:
        return THERAPIST_REGISTRY[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown therapist agent type: {agent_type}")


def register_therapist_configs(cs):
    for name, config_cls in THERAPIST_CONFIG_REGISTRY.items():
        cs.store(group="therapist", name=name, node=config_cls)


__all__ = [
    "BaseTherapist",
    "get_therapist",
    "register_therapist_configs",
]
