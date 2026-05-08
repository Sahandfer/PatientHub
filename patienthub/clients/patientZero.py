from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig


@dataclass
class PatientZeroClientConfig(APIModelConfig):
    """Configuration for the PatientZeroClient agent."""

    agent_name: str = "patientZero"
    prompt_path: str = "data/prompts/client/patientZero.yaml"
    data_path: str = "data/characters/PatientZero.json"
    data_idx: int = 0


class PatientZeroClient(BaseClient):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def build_sys_prompt(self):
        sys_prompt = self.prompts["sys_prompt"].render(data=self.data)
        self.messages = [{"role": "system", "content": sys_prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        return res
