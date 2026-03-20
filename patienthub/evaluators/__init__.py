from .base import LLMJudge, LLMJudgeConfig
from .conv import ConvJudge, ConvJudgeConfig
from .profile import ProfileJudge, ProfileJudgeConfig

from omegaconf import DictConfig

EVALUATOR_REGISTRY = {
    "conv_judge": ConvJudge,
    "profile_judge": ProfileJudge,
}
EVALUATOR_CONFIG_REGISTRY = {
    "conv_judge": ConvJudgeConfig,
    "profile_judge": ProfileJudgeConfig,
}


def get_evaluator(agent_name: str, configs: DictConfig = None, lang: str = "en"):
    print(f"Loading {agent_name} agent for evaluation...")
    if agent_name in EVALUATOR_REGISTRY:
        if configs is None:
            configs = get_evaluator_config(agent_name)
        configs.lang = lang
        return EVALUATOR_REGISTRY[agent_name](configs=configs)
    else:
        raise ValueError(f"Evaluator agent {agent_name} not found in registry.")


def get_evaluator_config(agent_name: str):
    if agent_name in EVALUATOR_CONFIG_REGISTRY:
        return EVALUATOR_CONFIG_REGISTRY[agent_name]()
    else:
        raise ValueError(f"Evaluator config for {agent_name} not found in registry.")


def register_evaluator_configs(cs):
    for name, config_cls in EVALUATOR_CONFIG_REGISTRY.items():
        cs.store(group="evaluator_configs", name=name, node=config_cls)


__all__ = [
    "get_evaluator",
    "get_evaluator_config",
    "register_evaluator_configs",
    "LLMJudge",
    "LLMJudgeConfig",
]
