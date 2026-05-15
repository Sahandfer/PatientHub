from typing import Any, Dict
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import LLMJudge, LLMJudgeConfig


@dataclass
class ProfileJudgeConfig(LLMJudgeConfig):
    agent_name: str = "profile_judge"
    prompt_path: str = "data/prompts/evaluator/client_profile.yaml"


class ProfileJudge(LLMJudge):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def evaluate(self, data: Dict[str, Any], *args) -> Dict[str, Any]:
        profile = data.get("profile", {})
        if not profile:
            print("No profile data provided for evaluation.")
            return {}

        return self.evaluate_dimensions(data)
