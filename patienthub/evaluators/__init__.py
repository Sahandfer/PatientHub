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


def get_evaluator(configs: DictConfig, lang: str = "en"):
    configs.lang = lang
    agent_type = configs.agent_type
    print(f"Loading {agent_type} agent for evaluation...")
    if agent_type in EVALUATOR_REGISTRY:
        return EVALUATOR_REGISTRY[agent_type](configs=configs)
    else:
        raise ValueError(f"Evaluator agent {agent_type} not found in registry.")


def register_evaluator_configs(cs):
    for name, config_cls in EVALUATOR_CONFIG_REGISTRY.items():
        cs.store(group="evaluator", name=name, node=config_cls)


__all__ = [
    "get_evaluator",
    "register_evaluator_configs",
    "LLMJudge",
    "LLMJudgeConfig",
]
