from typing import Dict, List
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model


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

        self.name = "CBT Therapist"

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="therapist", agent_type="CBT", lang=configs.lang
        )
        self.messages = [{"role": "system", "content": self.prompts["system"].render()}]

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client.get("name", "client")

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages).content
        self.messages.append({"role": "assistant", "content": res})

        return res

    def reset(self):
        self.messages = [{"role": "system", "content": self.prompts["system"].render()}]
        self.client = None
