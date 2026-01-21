from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field, create_model

from patienthub.utils import load_json
from patienthub.base import EvaluatorAgent


@dataclass
class SurveyEvaluatorConfig:
    """Configuration for Interview Evaluator."""

    target: str = "client"
    eval_type: str = "survey"
    questions_path: str = "data/evaluations/surveys/default_survey.json"


class SurveyEvaluator(EvaluatorAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.questions = load_json(configs.questions_path)
        self.current_q_idx = 0
        self.messages = []

    def get_next_question(self) -> str:
        if self.current_q_idx >= len(self.questions):
            return "[No more questions]"
        question = self.questions[self.current_q_idx]
        self.current_q_idx += 1
        return question

    def generate_response(self, msg: str) -> str:
        self.messages.append(msg)
        res = self.get_next_question()
        return res

    def evaluate(self, data: Any, *args) -> None:
        # evaluate based on ground truth or do calculations or sth
        pass

    def reset(self) -> None:
        self.current_q_idx = 0
        self.messages = []
