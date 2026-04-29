from .base import BaseTherapist
from .basic import BasicTherapist, BasicTherapistConfig
from .eliza import ElizaTherapist, ElizaTherapistConfig
from .user import UserTherapist, UserTherapistConfig
from .psyche import PsycheTherapist, PsycheTherapistConfig
from .cami import CamiTherapist, CamiTherapistConfig

import logging
from omegaconf import DictConfig

logger = logging.getLogger(__name__)

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
    if agent_name not in THERAPIST_REGISTRY:
        raise ValueError(f"Unknown therapist agent type: {agent_name}")
    if configs is None:
        configs = get_therapist_config(agent_name)
    configs.lang = lang
    try:
        therapist = THERAPIST_REGISTRY[agent_name](configs=configs)
    except Exception as e:
        logger.error("Failed to initialize therapist '%s': %s", agent_name, e, exc_info=True)
        raise ValueError(f"Error initializing therapist agent '{agent_name}'") from e
    logger.info(
        "Loaded therapist '%s' -> %s",
        agent_name,
        ", ".join(f"{k}={v}" for k, v in vars(configs).items()),
    )
    return therapist


def get_therapist_config(agent_name: str):
    if agent_name in THERAPIST_CONFIG_REGISTRY:
        return THERAPIST_CONFIG_REGISTRY[agent_name]()
    else:
        raise ValueError(f"Therapist config for {agent_name} not found in registry.")


def register_therapist_configs(cs):
    for name, config_cls in THERAPIST_CONFIG_REGISTRY.items():
        cs.store(group="therapist_configs", name=name, node=config_cls)


__all__ = [
    "BaseTherapist",
    "get_therapist",
    "get_therapist_config",
    "register_therapist_configs",
]
