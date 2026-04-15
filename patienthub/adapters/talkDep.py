# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for talkDep characters."""

from pydantic import Field

from .base import CharacterModel


class TalkDepSymptom(CharacterModel):
    name: str
    description: str
    severity: int


class TalkDepCharacter(CharacterModel):
    name: str
    age: int
    gender: str
    bdi_score: int
    depression_level: str
    key_negative_symptoms: list[TalkDepSymptom] = Field(default_factory=list)
    life_history: list[str] = Field(default_factory=list)
    social_context: list[str] = Field(default_factory=list)
    past_interactions: list[str] = Field(default_factory=list)
    linguistic_patterns: list[str] = Field(default_factory=list)
    emotional_tone: list[str] = Field(default_factory=list)
    typical_topics: list[str] = Field(default_factory=list)
    behavioral_constraints: list[str] = Field(default_factory=list)
    response_goals: list[str] = Field(default_factory=list)
    social_media_activity: list[str] = Field(default_factory=list)
    current_context_of_interaction: list[str] = Field(default_factory=list)
