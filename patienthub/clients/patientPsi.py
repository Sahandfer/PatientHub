from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class PatientPsiClientConfig(APIModelConfig):
    """Configuration for PatientPsi client agent."""

    agent_type: str = "patientPsi"
    prompt_path: str = "data/prompts/client/patientPsi.yaml"
    data_path: str = "data/characters/PatientPsi.json"
    data_idx: int = 0
    patient_type: str = "upset"


class PatientPsiClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    def build_sys_prompt(self):
        profile = self.prompts["profile"].render(data=self.data)
        patient_type = self.prompts["patientType"].render(
            patient_type=self.configs.patient_type
        )
        conv_prompt = self.prompts["conversation"].render(
            data=self.data, patientType=patient_type
        )
        self.messages = [{"role": "system", "content": profile + conv_prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
