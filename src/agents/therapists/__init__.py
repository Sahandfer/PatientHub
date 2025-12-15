from .basic import BasicTherapist
from .eliza import ElizaTherapist
from .user import UserTherapist
from .CBT import CBTTherapist

from omegaconf import DictConfig

THERAPISTS = {
    "basic": BasicTherapist,
    "eliza": ElizaTherapist,
    "user": UserTherapist,
    "CBT": CBTTherapist,
}


def get_therapist(configs: DictConfig):
    agent_type = configs.agent_type
    print(f"Loading {agent_type} therapist agent...")
    if agent_type in THERAPISTS:
        return THERAPISTS[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown therapist agent type: {agent_type}")


__all__ = [
    "BasicTherapist",
    "ElizaTherapist",
    "UserTherapist",
    "CBTTherapist",
]
