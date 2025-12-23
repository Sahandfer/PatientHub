from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class CBTTherapistConfig(APIModelConfig):
    """Configuration for CBT Therapist agent."""

    agent_type: str = "CBT"


class Response(BaseModel):
    reasoning: str = Field(
        description="The reasoning behind the generated response (no longer than 5 sentences)"
    )
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class CBTTherapist(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.name = "Therapist"

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="therapist", agent_type="CBT", lang=configs.lang
        )
        self.messages = [SystemMessage(content=self.prompts["system"].render())]

    def generate(self, messages: List[str], response_format: BaseModel):
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
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
