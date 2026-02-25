# coding=utf-8
# Licensed under the MIT License;

"""PSYCHE Client - Multi-faceted character for psychiatric assessment.

Paper: "A Multi-faceted Patient Simulation Framework for Evaluation of Psychiatric
       Assessment Conversational Agents" https://arxiv.org/pdf/2501.01594

PSYCHE provides comprehensive psychiatric profiles following standard assessment
formats. Profile components:

- MFC-Profile: Clinical info (identifying data, chief complaint, medical history)
- MFC-History: Narrative life history for context
- MFC-Behavior: Mental Status Examination (mood, affect, thought process)

Includes risk assessments for suicidal ideation, self-harm, and homicide.
"""

import json
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class PsycheClientConfig(APIModelConfig):
    """Configuration for Psyche client agent."""

    agent_type: str = "psyche"
    prompt_path: str = "data/prompts/client/psyche.yaml"
    data_path: str = "data/characters/Psyche.json"
    data_idx: int = 0


class PsycheClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = "PSYCHE-SP"

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    def build_sys_prompt(self):
        sys_prompt = self.prompts["system_prompt"].render(
            data={"mfc": json.dumps(self.data, ensure_ascii=False, indent=2)}
        )
        self.messages = [{"role": "system", "content": sys_prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
