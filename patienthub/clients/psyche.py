import json
from typing import Dict, List
from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class PsycheClientConfig(APIModelConfig):
    """Configuration for Psyche client agent."""

    agent_type: str = "psyche"
    data_path: str = "data/characters/Psyche.json"
    data_idx: int = 0


class PsycheClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = "PSYCHE-SP"

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="psyche", lang=configs.lang
        )
        self.build_sys_prompt()

    def build_sys_prompt(self):
        sys_prompt = self.prompts["system_prompt"].render(
            data={"mfc": json.dumps(self.data, ensure_ascii=False, indent=2)}
        )
        self.messages = [{"role": "system", "content": sys_prompt}]

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "Therapist")

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
