from typing import Dict, List
from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class TalkDepClientConfig(APIModelConfig):
    """
    Configuration for the TalkDepClient agent.
    """

    agent_type: str = "talkDep"
    data_path: str = "data/characters/talkDep.json"
    data_idx: int = 0


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
            {
                "role": "system",
                "content": self.prompts["sys_prompt"].render(data=self.data),
            }
        ]

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "therapist")

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.messages = []
        self.therapist = None
