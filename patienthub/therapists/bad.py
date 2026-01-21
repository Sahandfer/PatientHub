from typing import Dict, List
from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class BadTherapistConfig(APIModelConfig):
    """
    Configuration for the BadTherapist agent.
    """

    agent_type: str = "bad"
    data_path: str = "data/characters/therapists.json"
    data_idx: int = 0


class BadTherapist(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Bad Therapist")

        self.chat_model = get_chat_model(configs)
        self.prompt = load_prompts(
            role="therapist", agent_type="bad", lang=configs.lang
        )
        self.messages = [
            {
                "role": "system",
                "content": self.prompt.render(data=self.data),
            }
        ]

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client.get("name", "client")

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages).content
        self.messages.append({"role": "assistant", "content": res})

        return res

    def reset(self):
        self.messages = [
            {
                "role": "system",
                "content": self.prompt.render(data=self.data),
            }
        ]
        self.client = None
