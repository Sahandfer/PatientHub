from .eliza import ElizaTherapist, ElizaTherapistConfig
from .user import UserTherapist, UserTherapistConfig
from .CBT import CBTTherapist, CBTTherapistConfig
from .bad import BadTherapist, BadTherapistConfig
from .psyche import PsycheTherapist, PsycheTherapistConfig



from omegaconf import DictConfig

# Registry of therapist implementations
THERAPIST_REGISTRY = {
    "eliza": ElizaTherapist,
    "user": UserTherapist,
    "CBT": CBTTherapist,
    "bad": BadTherapist,
    "psyche": PsycheTherapist,
}

# Registry of therapist configs (for Hydra registration)
THERAPIST_CONFIG_REGISTRY = {
    "eliza": ElizaTherapistConfig,
    "user": UserTherapistConfig,
    "CBT": CBTTherapistConfig,
    "bad": BadTherapistConfig,
    "psyche": PsycheTherapistConfig,
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
    "get_therapist",
    "register_therapist_configs",
]
