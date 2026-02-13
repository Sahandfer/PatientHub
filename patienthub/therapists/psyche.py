from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseTherapist
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model


@dataclass
class PsycheTherapistConfig(APIModelConfig):
    """
    Configuration for the PsycheTherapist agent.
    """

    agent_type: str = "psyche"
    prompt_path: str = "data/prompts/therapist/psyche.yaml"


class PsycheTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.name = "Dr. Minsoo Kim"

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    def build_sys_prompt(self):
        self.messages = [
            {"role": "system", "content": self.prompts["sys_prompt"].render()}
        ]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
        self.client = None
