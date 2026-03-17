from typing import Any, Dict
from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.utils import flatten_conv
from .base import LLMJudge, LLMJudgeConfig


@dataclass
class ConvJudgeConfig(LLMJudgeConfig):
    agent_type: str = "conv_judge"
    granularity: str = "session"  # session, turn, turn_by_turn


class ConvJudge(LLMJudge):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        self.granularity = configs.granularity

    def evaluate(
        self, data: Dict[str, Any], target: str = "client", *args
    ) -> Dict[str, Any]:
        conv_history = data.get("messages", [])
        if not conv_history:
            print("No conversation history provided for evaluation.")
            return {}

        data["granularity"] = self.granularity

        data = {
            "conv_history": conv_history,
            "last_response": "",
        }

        if self.granularity == "session":
            data["conv_history"] = flatten_conv(conv_history)
            return self.evaluate_dimensions(data)

        elif self.granularity == "turn":
            data["conv_history"] = flatten_conv(conv_history[:-1])
            data["last_response"] = conv_history[-1].get("content", "")
            return self.evaluate_dimensions(data)

        elif self.granularity == "turn_by_turn":
            data["granularity"] = "turn"
            results = {}
            for i, turn in enumerate(conv_history):
                if turn.get("role", "").lower() == target.lower():
                    data["conv_history"] = self.flatten_conv(conv_history[:i])
                    data["last_response"] = turn.get("content", "")
                    res = self.evaluate_dimensions(data)
                    results[f"turn_{i}"] = res
            return results

        raise ValueError(f"Unknown granularity: {self.granularity}")
