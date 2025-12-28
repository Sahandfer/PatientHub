from typing import Dict, List
from dataclasses import dataclass
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class TalkDepClientConfig(APIModelConfig):
    """
    Configuration for the TalkDepClient agent.
    """

    agent_type: str = "talkDep"
    data_path: str = "data/characters/talkDep.json"
    data_idx: int = 0


class TalkDepClientResponse(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class TalkDepClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="talkDep", lang=configs.lang
        )
        self.messages = [
            SystemMessage(content=self.prompts["sys_prompt"].render(data=self.data))
        ]

    def generate(self, messages: List[str], response_format: BaseModel):
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "therapist")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=TalkDepClientResponse)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.messages = []
        self.therapist = None
