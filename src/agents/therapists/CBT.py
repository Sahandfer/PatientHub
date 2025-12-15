from typing import Dict, List
from pydantic import BaseModel, Field

from src.agents import InferenceAgent
from src.utils import load_prompts, get_model_client

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Response(BaseModel):
    reasoning: str = Field(
        description="The reasoning behind the generated response (no longer than 5 sentences)"
    )
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class CBTTherapist(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.name = "Therapist"

        self.model_client = get_model_client(configs)
        self.prompts = load_prompts(
            role="therapist", agent_type="CBT", lang=configs.lang
        )
        self.messages = [SystemMessage(content=self.prompts["system"].render())]

    def generate(self, messages: List[str], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client.get("name", "client")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.messages = [SystemMessage(content=self.prompts["system"])]
        self.client = None
