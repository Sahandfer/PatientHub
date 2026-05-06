# coding=utf-8
# Licensed under the MIT License;

"""Psyche Therapist - Structured psychiatric interview agent.

A prompt-driven psychiatrist that conducts intake-style clinical interviews.

Key Features:
- Structured interview format following psychiatric assessment standards
- System prompt with explicit clinical assessment criteria
- Suitable for psychiatric evaluation training simulations
"""

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseTherapist
from patienthub.configs import APIModelConfig


@dataclass
class PsycheTherapistConfig(APIModelConfig):
    """
    Configuration for the PsycheTherapist agent.
    """

    agent_name: str = "psyche"
    prompt_path: str = "data/prompts/therapist/psyche.yaml"


class PsycheTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        self.name = "Dr. Minsoo Kim"

    def build_sys_prompt(self):
        self.messages = [
            {"role": "system", "content": self.prompts["sys_prompt"].render()}
        ]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res
