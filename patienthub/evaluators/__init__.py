from .client import get_client_evaluator, CLIENT_EVALUATOR_CONFIG_REGISTRY
from .therapist import get_therapist_evaluator, THERAPIST_EVALUATOR_CONFIG_REGISTRY

from omegaconf import DictConfig

# Combined registry of all evaluator configs (for Hydra registration)
EVALUATOR_CONFIG_REGISTRY = {
    **{f"client_{k}": v for k, v in CLIENT_EVALUATOR_CONFIG_REGISTRY.items()},
    **{f"therapist_{k}": v for k, v in THERAPIST_EVALUATOR_CONFIG_REGISTRY.items()},
}


def get_evaluator(configs: DictConfig):
    agent_type = configs.agent_type
    if agent_type == "therapist":
        return get_therapist_evaluator(configs)
    elif agent_type == "client":
        return get_client_evaluator(configs)
    else:
        raise ValueError(f"Evaluation for {agent_type} is not supported")


def register_evaluator_configs(cs):
    for name, config_cls in EVALUATOR_CONFIG_REGISTRY.items():
        cs.store(group="evaluator", name=name, node=config_cls)


__all__ = [
    "get_evaluator",
    "register_evaluator_configs",
]
