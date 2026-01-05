from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class SAPSClientConfig(APIModelConfig):
    """Configuration for the SAPSClient agent."""

    agent_type: str = "saps"
    data_path: str = "data/characters/SAPS.json"
    data_idx: int = 0


# Pydantic models for state detection and response
class StageIResponse(BaseModel):
    """Stage I: five types of questions classification"""

    question_type: Literal["A", "B", "C", "D", "E"] = Field()


class StageIIResponse(BaseModel):
    """Stage II: determine the question is specific or broad"""

    specificity: Literal["Specific", "Broad"] = Field(
        description="Whether the question/advise is Specific or Broad"
    )


class StageIIIResponse(BaseModel):
    """Stage III: Memory extraction"""

    has_relevant_info: bool = Field(
        description="Whether there is relevant information in the medical record"
    )
    extracted_text: str = Field(
        default="",
        description="The extracted text fragment, if there is no relevant information, it is empty",
    )


class FinalResponse(BaseModel):
    """Patient final response"""

    content: str = Field(description="The content of the patient's response")


class SAPSClient(ChatAgent):
    """State-Aware Patient Simulator Client.

    Implement three-stage state detection process:
    1. Stage I: classify the doctor's questions into five types: A/B/C/D/E
    2. Stage II: determine the question is specific or broad (only A/B)
    3. Stage III: extract relevant information from the complete medical record (only A-A/B-A)
    4. Select the corresponding state_instruction prompt based on the final state (A-A-A/A-A-B/A-B/B-A-A/B-A-B/B-B)
    5. Generate client's response and update the history
    """

    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(role="client", agent_type="saps", lang=configs.lang)

        self.messages: List[Any] = []

    def set_therapist(
        self,
        therapist: Dict[str, Any],
        prev_sessions: List[Dict[str, str]] | None = None,
    ):
        self.therapist = therapist.get("name", "Therapist")

    def generate(self, messages: List[Any], response_format: BaseModel) -> BaseModel:
        """Generate response using structured output"""
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res

    def perform_stage_I(self, question: str) -> StageIResponse:
        prompt = self.prompts["state_detection"]["stage_I"].render(question=question)
        res = self.generate(
            messages=[SystemMessage(content=prompt)], response_format=StageIResponse
        )
        return res.question_type

    def perform_stage_II(self, question: str, question_type: str) -> StageIIResponse:
        if question_type not in ["A", "B"]:
            return ""

        prompt = self.prompts["state_detection"]["stage_II"][question_type].render(
            question=question
        )
        res = self.generate(
            messages=[SystemMessage(content=prompt)], response_format=StageIIResponse
        )
        return "A" if res.specificity == "Specific" else "B"

    def perform_stage_III(
        self,
        question: str,
        question_type: str,
        specificity: str,
    ) -> StageIIIResponse:
        if specificity != "A":
            return "", ""

        prompt = self.prompts["state_detection"]["stage_III"][question_type].render(
            question=question, patient_info=self.data["patient_info"]
        )
        res = self.generate(
            messages=[SystemMessage(content=prompt)], response_format=StageIIIResponse
        )
        memory = res.extracted_text if res.has_relevant_info else ""
        return memory, "A" if memory else "B"

    def get_state(self, msg: str):
        # Stage I
        q_type = self.perform_stage_I(msg)
        # Stage II
        specificity = self.perform_stage_II(msg, question_type=q_type)
        # Stage III
        memory, has_memory = self.perform_stage_III(
            msg, question_type=q_type, specificity=specificity
        )

        state = "-".join([q_type, specificity, has_memory]).strip("-")

        return state, memory

    def generate_response(self, msg: str) -> FinalResponse:
        self.messages.append(HumanMessage(content=msg))

        state, memory = self.get_state(msg)

        prompt = self.prompts["state_instruction"][state].render(patient_info=memory)

        messages = [SystemMessage(content=prompt)] + self.messages

        res = self.generate(messages=messages, response_format=FinalResponse)

        self.messages.append(AIMessage(content=res.content))

        return res

    def reset(self):
        self.messages = []
        self.therapist = None
