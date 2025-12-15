from typing import Dict, List
from pydantic import BaseModel, Field

from src.agents import InferenceAgent
from src.utils import load_prompts, load_json, get_model_client

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class PatientPsiClient(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.model_client = get_model_client(configs)
        self.prompts = load_prompts(
            role="client", agent_type="patientPsi", lang=configs.lang
        )
        self.messages = [
            SystemMessage(content=self.prompts["profile"].render(data=self.data))
        ]

    def generate(self, messages: List[str], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "Therapist")

    def generate_response(self, msg: str):
        if len(self.messages) == 1:
            patient_type_content = self.prompts["patientType"].render(
                patient_type=self.configs.patient_type
            )
            self.messages[0].content += "\n" + self.prompts["conversation"].render(
                data=self.data,
                patientType=self.configs.patient_type,
                patientTypeContent=patient_type_content,
            )

        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.messages = []
        self.therapist = None
