from typing import Any, Dict
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import LLMJudge, LLMJudgeConfig


@dataclass
class ProfileJudgeConfig(LLMJudgeConfig):
    agent_type: str = "profile_judge"


class ProfileJudge(LLMJudge):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def evaluate(self, data: Any, *args) -> Dict[str, Any]:
        profile = data.get("profile", {})
        if not profile:
            print("No profile data provided for evaluation.")
            return {}

        return self.evaluate_dimensions(data)
