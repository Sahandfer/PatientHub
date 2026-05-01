# coding=utf-8
# Licensed under the MIT License;

"""ClientCast Generator - Creates diverse psychological profiles from conversations.

Paper: "Towards a Client-Centered Assessment of LLM Therapists by Client Simulation"
       https://arxiv.org/pdf/2406.12266

Generates ClientCast character files with detailed psychological assessments.

Key Features:
- Big Five personality trait extraction from conversation excerpts
- Symptom identification using PHQ-9, GAD-7, OQ-45 scales
- Demographic and clinical profile inference
- Diversity-focused batch generation capabilities
"""

from typing import Any, Dict, Literal, Optional
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict, Field

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, save_json
from patienthub.schemas.clientCast import BasicProfile, BigFive, ClientCastCharacter


@dataclass
class ClientCastGeneratorConfig(APIModelConfig):
    """Configuration for ClientCast generator."""

    agent_name: str = "clientCast"
    prompt_path: str = "data/prompts/generator/clientCast.yaml"
    input_dir: str = "data/resources/ClientCast/human_data.json"
    symptoms_dir: str = "data/resources/ClientCast/symptoms.json"
    output_dir: str = "data/characters/ClientCast.json"
    data_idx: int = 0


class SymptomEstimate(BaseModel):
    identified: bool = Field(
        ...,
        description=(
            "Whether the symptom can be identified from the conversation prior to it."
        ),
    )
    severity_level: Optional[int] = Field(
        ...,
        description="Severity level as an integer (0-3) if identified is true, otherwise null",
    )
    severity_label: Optional[
        Literal[
            "Not at all", "Several days", "More than half the days", "Nearly everyday"
        ]
    ] = Field(
        ...,
        description=(
            "label matching the severity_level if identified is true, otherwise null"
        ),
        example="More than half the days",
    )
    explanation: str = Field(
        ...,
        description=(
            "Brief and clear explanation. Do not reference the therapist/session/conversation explicitly."
        ),
    )


class OQ45Estimate(SymptomEstimate):
    identified: bool = Field(
        ...,
        description=(
            "Whether the symptom can be identified from the conversation prior to it."
        ),
    )
    scale_type: Literal["positive", "negative"] = Field(
        ...,
        description=(
            "Which severity key applies for this OQ-45 item "
            "(positive severity vs negative severity)."
        ),
        example="negative",
    )
    severity_level: Optional[int] = Field(
        ...,
        description="Severity level as an integer (0-3) if identified is true, otherwise null",
    )
    severity_label: Optional[
        Literal["Never", "Rarely", "Sometimes", "Frequently", "Always"]
    ] = Field(
        ...,
        description=(
            "label matching the severity_level if identified is true, otherwise null"
        ),
        example="More than half the days",
    )
    explanation: str = Field(
        ...,
        description=(
            "Brief and clear explanation. Do not reference the therapist/session/conversation explicitly."
        ),
    )


class Symptoms(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    PHQ_9: Dict[str, SymptomEstimate] = Field(
        ...,
        alias="PHQ-9",
        description="PHQ-9 item estimates keyed by item number as string.",
    )
    GAD_7: Dict[str, SymptomEstimate] = Field(
        ...,
        alias="GAD-7",
        description="GAD-7 item estimates keyed by item number as string.",
    )
    OQ_45: Dict[str, OQ45Estimate] = Field(
        ...,
        alias="OQ-45",
        description="OQ-45 item estimates keyed by item number as string.",
    )


class ClientCastGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        self.conv_history = self.load_data()
        self.symptoms = load_json(self.configs.symptoms_dir)

    def load_data(self):
        data = load_json(self.configs.input_dir)[self.configs.data_idx]
        return "\n".join(
            [f"{msg['role']}: {msg['content']}\n" for msg in data.get("messages", [])]
        ).strip()

    def generate_basic_profile(self):
        prompt = self.prompts["basic_profile_prompt"].render(
            conversation=self.conv_history
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=BasicProfile
        )
        return res

    def generate_big_five(self):
        prompt = self.prompts["big_five_prompt"].render(conversation=self.conv_history)
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=BigFive
        )
        return res

    def generate_symptoms(self):
        full_res = {}
        for disorder, symptoms in self.symptoms.items():
            for i, symptom in enumerate(symptoms):
                prompt = self.prompts["symptoms_prompt"].render(
                    conversation=self.conv_history, symptom=symptom
                )
                if disorder == "OQ-45":
                    res = self.chat_model.generate(
                        [{"role": "system", "content": prompt}],
                        response_format=OQ45Estimate,
                    )
                else:
                    res = self.chat_model.generate(
                        [{"role": "system", "content": prompt}],
                        response_format=SymptomEstimate,
                    )
                full_res[disorder] = {f"{i+1}": res}
                # For the sake of API cost, we only do this for one symptom from each disorder
                break

        return Symptoms(
            PHQ_9=full_res["PHQ-9"],
            GAD_7=full_res["GAD-7"],
            OQ_45=full_res["OQ-45"],
        )

    def generate_character(self) -> Dict[str, Any]:
        basic_profile = self.generate_basic_profile()
        big_five = self.generate_big_five()
        symptoms = self.generate_symptoms()

        character = ClientCastCharacter(
            basic_profile=basic_profile,
            big_five=big_five,
            symptoms=symptoms,
        )

        save_json(
            data={
                **character.model_dump(),
                "symptoms": character.symptoms.model_dump(by_alias=True),
            },
            output_dir=self.configs.output_dir,
        )
