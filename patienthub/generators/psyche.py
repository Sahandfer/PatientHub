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

from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, save_json
from patienthub.schemas.psyche import MFCProfile, MFCBehavior, PsycheCharacter


@dataclass
class PsycheGeneratorConfig(APIModelConfig):
    """Configuration for Psyche generator."""

    agent_name: str = "psyche"
    prompt_path: str = "data/prompts/generator/psyche.yaml"
    input_dir: str = "data/resources/psyche_character.json"
    output_dir: str = "data/characters/Psyche MFC.json"


class MFCHistory(BaseModel):
    MFC_History: str = Field(..., alias="MFC-History")


class PsycheGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        self.data = load_json(configs.generator.input_dir)
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
            [{"role": "system", "content": prompt}], responses_format=MFCProfile
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
            [{"role": "system", "content": prompt}], responses_format=MFCHistory
        )

    def generate_mfc_behavior(self):
        profile_json = self.mfc_profile.model_dump_json(by_alias=True)
        history_json = self.mfc_history.model_dump_json(by_alias=True)
        prompt = self.prompts["MFC_Behavior"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
            mfc_profile_json=profile_json,
            mfc_history_json=history_json,
        )
        self.mfc_behavior = self.chat_model.generate(
            [{"role": "system", "content": prompt}], responses_format=MFCBehavior
        )

    def generate_character(self):
        self.generate_mfc_profile()
        self.generate_mfc_history()
        self.generate_mfc_behavior()

        mfc = PsycheCharacter(
            **{"MFC-Profile": self.mfc_profile, "MFC-History": self.mfc_history.MFC_History, "MFC-Behavior": self.mfc_behavior}
        )

        save_json(
            data=mfc.model_dump(by_alias=True),
            output_dir=self.configs.generator.output_dir,
        )

    def reset(self):
        self.mfc_profile = None
        self.mfc_history = None
        self.mfc_behavior = None
