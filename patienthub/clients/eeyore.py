# coding=utf-8
# Licensed under the MIT License;

"""Eeyore Client - Realistic depression simulation via expert-optimized model.

Paper: "Eeyore: Realistic Depression Simulation via Expert-in-the-Loop Supervised
       and Preference Optimization" (ACL 2025 Findings)
       https://aclanthology.org/2025.findings-acl.707/

Eeyore uses a fine-tuned model (instruction tuning + DPO) to simulate individuals
experiencing depression.

Key features:
- Real-world depression data (Reddit, counseling transcripts)
- DSM-V standards and Beck's cognitive theory profiles
- Expert-in-the-loop preference optimization
"""

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, load_prompts, get_chat_model


@dataclass
class EeyoreClientConfig(APIModelConfig):
    """Configuration for Eeyore client agent (local model)."""

    agent_type: str = "eeyore"
    prompt_path: str = "data/prompts/client/eeyore.yaml"
    data_path: str = "data/characters/Eeyore.json"
    model_type: str = "LOCAL"
    model_name: str = "hosted_vllm//<path_to_weights>/Eeyore_llama3.1_8B"
    data_idx: int = 0


class EeyoreClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "EeyoreClient")
        self.profile = self.data.get("profile", {})

        self.chat_model = get_chat_model(configs)

        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    def build_sys_prompt(self):
        sys_prompt = self.prompts["system_prompt"].render(profile=self.profile)
        self.messages = [{"role": "system", "content": sys_prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
