from ..base import BaseAgent
from utils import load_prompts
from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel


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


class CBTEvaluator(BaseAgent):
    def __init__(self, model_client: BaseChatModel, lang: str = "en"):
        self.lang = lang
        self.role = "evaluator"
        self.agent_type = "cbt"
        self.model_client = model_client
        self.prompt = load_prompts(
            role=self.role, agent_type=self.agent_type, lang=self.lang
        )["prompt"]

    def generate(self, messages: List[Dict]):
        messages = [f"{msg['role']}: {msg['content']}" for msg in messages]
        model_client = self.model_client.with_structured_output(CBTFeedback)
        self.prompt = self.prompt.render(dialogue_history="\n".join(messages))
        res = model_client.invoke(self.prompt)
        return res

    def reset(self):
        pass
