# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for adaptiveVP characters."""

from pydantic import Field

from .base import CharacterModel


class AdaptiveVPCharacter(CharacterModel):
    id: int | str | None = None
    type: int | str | None = None
    type_text: str = Field(default="", alias="type-text")
    name: str
    situation: str
    chief_complaint: str = Field(default="", alias="Chief complaint")
    gender: str = ""
    age: int | None = None
    religion: str = ""
    height: str = ""
    weight: str = ""
    main_symptom: str = Field(default="", alias="Main symptom")
    history_of_present_illness: str = Field(
        default="",
        alias="History of present illness",
    )
    social_history: str = Field(default="", alias="social history")
    past_medical_history: str = Field(default="", alias="past medical history")
    past_surgical_history_and_date: str = Field(
        default="",
        alias="past surgical history & date",
    )
    family_medical_history: str = Field(default="", alias="family medical history")
    allergies: str = ""
    immunization: str = ""
    medication: str = ""
    primary_diagnosis: str = Field(default="", alias="primary diagnosis")
    communication_summary: str = ""
    first_statement: str = ""
