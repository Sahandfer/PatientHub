from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class PatientPsiClientConfig(APIModelConfig):
    """Configuration for PatientPsi client agent."""

    agent_type: str = "patientPsi"
    data_path: str = "data/characters/PatientPsi.json"
    data_idx: int = 0
    patient_type: str = "upset"


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class PatientPsiClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="patientPsi", lang=configs.lang
        )
        self.load_sys_prompt()

    def load_sys_prompt(self):
        profile = self.prompts["profile"].render(data=self.data)
        patient_type = self.prompts["patientType"].render(
            patient_type=self.configs.patient_type
        )
        conv_prompt = self.prompts["conversation"].render(
            data=self.data, patientType=patient_type
        )
        self.messages = [SystemMessage(content=profile + conv_prompt)]

    def generate(self, messages: List[str], response_format: BaseModel):
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "Therapist")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.load_sys_prompt()
        self.therapist = None
