# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for simPatient characters."""

from pydantic import Field

from .base import CharacterModel


class SimPatientPersona(CharacterModel):
    gender: str
    ethnicity: str
    age: int
    occupation: str
    mbti: str


class SimPatientCognitiveModel(CharacterModel):
    patient_control: int = Field(ge=1, le=10)
    patient_efficacy: int = Field(ge=1, le=10)
    patient_awareness: int = Field(ge=1, le=10)
    patient_reward: int = Field(ge=1, le=10)


class SimPatientCharacter(CharacterModel):
    persona: SimPatientPersona
    cognitive_model: SimPatientCognitiveModel
    between_session_event: str = ""
