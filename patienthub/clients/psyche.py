import json
from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class PsycheClientConfig(APIModelConfig):
    """Configuration for Psyche client agent."""

    agent_type: str = "psyche"
    data_path: str = "data/characters/Psyche.json"
    data_idx: int = 0


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class PsycheClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = "PSYCHE-SP"

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="psyche", lang=configs.lang
        )

        self.sys_prompt = self.prompts["PSYCHE_SP_prompt"].render(
            data={"mfc": json.dumps(self.data, ensure_ascii=False, indent=2)}
        )
        self.messages = [SystemMessage(content=self.sys_prompt)]

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
        self.therapist = None
        self.messages = [SystemMessage(content=self.sys_prompt)]
