from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model

from omegaconf import DictConfig


@dataclass
class ActiveListeningEvaluatorConfig(APIModelConfig):
    """Configuration for Active Listening Evaluator."""

    agent_type: str = "therapist"
    eval_type: str = "activeListening"
    temperature: float = 0.4
    input_dir: str = ""
    output_dir: str = ""


class DimensionFeedback(BaseModel):
    strengths: List[str] = Field(
        description="A list of specific strengths demonstrated by the therapist in this dimension (2-3 items)",
    )
    areas_for_improvement: List[str] = Field(
        description="A list of specific areas for improvement for the therapist in this dimension (2-3 items)",
    )


class ActiveListeningDimensions(BaseModel):
    empathic_understanding: DimensionFeedback = Field(
        description="Evaluation of the therapist's demonstration of empathic understanding",
    )
    unconditional_positive_regard: DimensionFeedback = Field(
        description="Evaluation of the therapist's demonstration of unconditional positive regard",
    )
    congruence: DimensionFeedback = Field(
        description="Evaluation of the therapist's demonstration of congruence",
    )


class ActiveListeningFeedback(BaseModel):
    overall_score: int = Field(
        description="Overall score for the therapist's active listening skills in this session",
    )
    summary: str = Field(
        description="A brief summary of the therapist's performance regarding active listening skills  (you should reference what the therapist said/do in the session that makes you give this rating)",
    )
    dimension_feedback: ActiveListeningDimensions = Field(
        description="Detailed feedback for each active listening dimension"
    )


class ActiveListeningEvaluator(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.chat_model = get_chat_model(configs)
        self.prompt = load_prompts(
            role="evaluator/therapist", agent_type="activeListening", lang=configs.lang
        )["prompt"]

    def generate(self, messages: List[Dict]):
        messages = [f"{msg['role']}: {msg['content']}" for msg in messages]
        chat_model = self.chat_model.with_structured_output(ActiveListeningFeedback)
        self.prompt = self.prompt.render(dialogue_history="\n".join(messages))
        res = chat_model.invoke(self.prompt)

        return res

    def reset(self):
        pass
