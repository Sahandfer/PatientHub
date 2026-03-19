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


def get_therapist(agent_name: str, configs: DictConfig = None, lang: str = "en"):
    print(f"Loading {agent_name} therapist agent...")
    if agent_name in THERAPIST_REGISTRY:
        if configs is None:
            configs = get_therapist_config(agent_name)
        configs.lang = lang
        return THERAPIST_REGISTRY[agent_name](configs=configs)
    else:
        raise ValueError(f"Unknown therapist agent type: {agent_name}")


def get_therapist_config(agent_name: str):
    if agent_name in THERAPIST_CONFIG_REGISTRY:
        return THERAPIST_CONFIG_REGISTRY[agent_name]()
    else:
        raise ValueError(f"Therapist config for {agent_name} not found in registry.")


def register_therapist_configs(cs):
    for name, config_cls in THERAPIST_CONFIG_REGISTRY.items():
        cs.store(group="therapist", name=name, node=config_cls)


__all__ = [
    "BaseTherapist",
    "get_therapist",
    "get_therapist_config",
    "register_therapist_configs",
]
