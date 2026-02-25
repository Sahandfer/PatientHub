# coding=utf-8
# Licensed under the MIT License;

"""TalkDep Client - BDI-grounded personas for depression screening.

Paper: "Clinically Grounded LLM Personas for Conversation-Centric Depression
       Screening" (CIKM 2025) https://dl.acm.org/doi/10.1145/3746252.3761617

TalkDep creates clinically grounded personas based on Beck Depression Inventory-II
(BDI-II).

Key Features:
- BDI scores as ground truth for simulation evaluation
- 12 validated personas across 4 severity levels
- Severity levels: Minimal (0-9), Mild (10-18), Moderate (19-29), Severe (30-63)
- Detailed symptom profiles with linguistic/behavioral patterns
"""

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class TalkDepClientConfig(APIModelConfig):
    """Configuration for the TalkDepClient agent."""

    agent_type: str = "talkDep"
    prompt_path: str = "data/prompts/client/talkDep.yaml"
    data_path: str = "data/characters/talkDep.json"
    data_idx: int = 0


class TalkDepClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    def build_sys_prompt(self):
        self.messages = [
            {
                "role": "system",
                "content": self.prompts["sys_prompt"].render(data=self.data),
            }
        ]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
