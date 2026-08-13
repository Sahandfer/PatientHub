from typing import Any, Dict
from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.utils.logger import get_logger
from .base import LLMJudge, LLMJudgeConfig

logger = get_logger(__name__)


@dataclass
class ProfileJudgeConfig(LLMJudgeConfig):
    agent_name: str = "profile_judge"
    prompt_path: str = "data/prompts/evaluator/client_profile.yaml"


class ProfileJudge(LLMJudge):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def evaluate(self, data: Dict[str, Any], *args) -> Dict[str, Any]:
        if not data:
            logger.warning("No profile data provided for evaluation.")
            return {}

        return self.evaluate_dimensions(data)
