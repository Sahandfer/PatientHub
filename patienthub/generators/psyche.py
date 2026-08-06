# coding=utf-8
# Licensed under the MIT License;

"""PSYCHE Generator - Creates multi-faceted psychiatric character profiles.

Paper: "A Multi-faceted Patient Simulation Framework for Evaluation of Psychiatric
       Assessment Conversational Agents" https://arxiv.org/pdf/2501.01594

Generates comprehensive psychiatric profiles (MFC) for assessment training.

Profile components:
- MFC-Profile: Identifying data, chief complaint, medical/social history
- MFC-History: Narrative life history with triggering events
- MFC-Behavior: Mental Status Examination (mood, affect, thought process)
- Risk assessments: Suicidal ideation, self-harm, homicide risk ratings
"""

from typing import Any
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.schemas.psyche import MFCProfile, MFCBehavior, PsycheCharacter


@dataclass
class PsycheGeneratorConfig(APIModelConfig):
    """Configuration for Psyche generator."""

    agent_name: str = "psyche"
    prompt_path: str = "data/prompts/generator/psyche.yaml"


class PsycheGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        self.mfc_profile = None
        self.mfc_history = None
        self.mfc_behavior = None

    def generate_mfc_profile(self):
        prompt = self.prompts["MFC_Profile"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
        )
        self.mfc_profile = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=MFCProfile
        )

    def generate_mfc_history(self):
        profile_json = self.mfc_profile.model_dump_json(by_alias=True)
        prompt = self.prompts["MFC_History"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
            mfc_profile_json=profile_json,
        )
        self.mfc_history = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=str
        )

    def generate_mfc_behavior(self):
        profile_json = self.mfc_profile.model_dump_json(by_alias=True)
        prompt = self.prompts["MFC_Behavior"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
            mfc_profile_json=profile_json,
            mfc_history_json=self.mfc_history,
        )
        self.mfc_behavior = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=MFCBehavior
        )

    def generate_character(self, data: dict[str, Any]) -> PsycheCharacter:
        self.data = data

        self.generate_mfc_profile()
        self.generate_mfc_history()
        self.generate_mfc_behavior()

        return PsycheCharacter(
            **{
                "MFC-Profile": self.mfc_profile,
                "MFC-History": self.mfc_history,
                "MFC-Behavior": self.mfc_behavior,
            }
        )
