from .base import LLMJudge, LLMJudgeConfig
from .conv import ConvJudge, ConvJudgeConfig
from .profile import ProfileJudge, ProfileJudgeConfig

import logging
from omegaconf import DictConfig

logger = logging.getLogger(__name__)

EVALUATOR_REGISTRY = {
    "conv_judge": ConvJudge,
    "profile_judge": ProfileJudge,
}
EVALUATOR_CONFIG_REGISTRY = {
    "conv_judge": ConvJudgeConfig,
    "profile_judge": ProfileJudgeConfig,
}


def get_evaluator(agent_name: str, configs: DictConfig = None, lang: str = "en"):
    if agent_name not in EVALUATOR_REGISTRY:
        raise ValueError(f"Evaluator agent '{agent_name}' not found in registry.")
    if configs is None:
        configs = get_evaluator_config(agent_name)
    configs.lang = lang
    try:
        evaluator = EVALUATOR_REGISTRY[agent_name](configs=configs)
    except Exception as e:
        logger.error("Failed to initialize evaluator '%s': %s", agent_name, e, exc_info=True)
        raise ValueError(f"Error initializing evaluator agent '{agent_name}'") from e
    logger.info("Loaded evaluator '%s'", agent_name)
    return evaluator


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
