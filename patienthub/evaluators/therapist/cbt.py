from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model

from omegaconf import DictConfig


@dataclass
class CBTEvaluatorConfig(APIModelConfig):
    """Configuration for CBT Evaluator."""

    agent_type: str = "therapist"
    eval_type: str = "cbt"
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


class CBTDimensions(BaseModel):
    identification_of_core_beliefs: DimensionFeedback = Field(
        description="Evaluation of the therapist's ability to identify core beliefs",
    )
    socratic_questioning: DimensionFeedback = Field(
        description="Evaluation of the therapist's use of Socratic questioning",
    )
    actionable_homework: DimensionFeedback = Field(
        description="Evaluation of the therapist's collaboration on actionable homework",
    )
    cognitive_restructuring: DimensionFeedback = Field(
        description="Evaluation of the therapist's use of cognitive restructuring techniques",
    )


class CBTFeedback(BaseModel):
    overall_score: int = Field(
        description="Overall score for the therapist's CBT skills in this session",
    )
    summary: str = Field(
        description="A brief summary of the therapist's performance (you should reference what the therapist said/do in the session that makes you give this rating)",
    )
    dimension_feedback: CBTDimensions = Field(
        description="Detailed scores for each CBT dimension"
    )


class CBTEvaluator(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.chat_model = get_chat_model(configs)
        self.prompt = load_prompts(
            role="evaluator/therapist", agent_type="cbt", lang=configs.lang
        )["prompt"]

    def generate(self, messages: List[Dict]):
        messages = [f"{msg['role']}: {msg['content']}" for msg in messages]
        chat_model = self.chat_model.with_structured_output(CBTFeedback)
        self.prompt = self.prompt.render(dialogue_history="\n".join(messages))
        res = chat_model.invoke(self.prompt)

        return res

    def reset(self):
        pass
