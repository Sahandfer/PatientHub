# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for clientCast characters."""

from typing import Dict, Literal

from pydantic import Field

from .base import CharacterModel


class ClientCastCharacter(CharacterModel):
    class BasicProfile(CharacterModel):
        name: str
        gender: str
        age: int
        age_explain: str
        occupation: str
        topic: str
        situation: str
        emotion: str
        reasons: str
        problem: str
        emotion_trigger: str
        feeling_expression: str
        emotional_fluctuation: str
        resistance: str

    class BigFive(CharacterModel):
        class Trait(CharacterModel):
            score_percent: int = Field(ge=0, le=100)
            explanation: str

        Openness: Trait
        Conscientiousness: Trait
        Extraversion: Trait
        Agreeableness: Trait
        Neuroticism: Trait

    class Symptoms(CharacterModel):
        class Estimate(CharacterModel):
            identified: bool
            severity_level: int | None = None
            severity_label: str | None = None
            explanation: str

        class OQ45Estimate(Estimate):
            scale_type: Literal["positive", "negative"]

        PHQ_9: Dict[str, Estimate] = Field(alias="PHQ-9")
        GAD_7: Dict[str, Estimate] = Field(alias="GAD-7")
        OQ_45: Dict[str, OQ45Estimate] = Field(alias="OQ-45")

    basic_profile: BasicProfile
    big_five: BigFive
    symptoms: Symptoms
