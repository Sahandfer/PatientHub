# coding=utf-8
# Licensed under the MIT License;

"""PatientPsi Client - CBT-grounded patient simulation.

Paper: "PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training
       Mental Health Professionals" (EMNLP 2024 Main)
       https://aclanthology.org/2024.emnlp-main.711/

PatientPsi simulates patients with CBT cognitive models including core beliefs,
intermediate beliefs, and automatic thoughts.

Key Features:
- CBT cognitive conceptualization (history, beliefs, coping strategies)
- 6 conversational styles: plain, upset, verbose, reserved, tangent, pleasing
"""

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig


@dataclass
class PatientPsiClientConfig(APIModelConfig):
    """Configuration for PatientPsi client agent."""

    agent_name: str = "patientPsi"
    prompt_path: str = "data/prompts/client/patientPsi.yaml"
    data_path: str = "data/characters/PatientPsi.json"
    data_idx: int = 0
    patient_type: str = "plain"


class PatientPsiClient(BaseClient):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def build_sys_prompt(self):
        profile = self.prompts["profile"].render(data=self.data)
        patient_type_content = self.prompts["patientType"].render(
            patient_type=self.configs.patient_type
        )
        conv_prompt = self.prompts["conversation"].render(
            data=self.data,
            patientType=self.configs.patient_type,
            patientTypeContent=patient_type_content,
        )
        self.messages = [{"role": "system", "content": profile + conv_prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res
