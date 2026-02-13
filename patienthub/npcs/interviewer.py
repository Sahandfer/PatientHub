from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.utils import load_json


@dataclass
class InterviewerEvaluatorConfig:
    """Configuration for Interview Evaluator."""

    agent_type: str = "Interviewer"
    data: str = "data/evaluations/surveys/default_survey.json"


class InterviewerNPC:
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.data = load_json(configs.data)
        self.current_q_idx = 0
        self.messages = []

    def get_next_question(self) -> str:
        if self.current_q_idx >= len(self.data):
            return "[No more questions]"
        question = self.data[self.current_q_idx]
        self.current_q_idx += 1
        return question

    def generate_response(self, msg: str) -> str:
        self.messages.append(msg)
        res = self.get_next_question()
        return res

    def reset(self) -> None:
        self.current_q_idx = 0
        self.messages = []
