# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for Eeyore characters."""

from typing import Any, Dict

from pydantic import Field

from .base import CharacterModel


class EeyoreConversationTurn(CharacterModel):
    role: str
    content: str


class EeyoreCognitiveModelEntry(CharacterModel):
    situation: str = ""
    automatic_thoughts: str = ""
    emotion: str = ""
    behavior: str = ""


class EeyoreCognitiveProfile(CharacterModel):
    life_history: str = ""
    core_beliefs: str = ""
    core_belief_description: str = ""
    intermediate_beliefs: str = ""
    intermediate_beliefs_during_depression: str = ""
    coping_strategies: str = ""
    cognitive_models: list[EeyoreCognitiveModelEntry] = Field(default_factory=list)


class EeyoreCharacter(CharacterModel):
    name: str = "EeyoreClient"
    conversation: list[EeyoreConversationTurn] = Field(default_factory=list)
    source: str | None = None
    id_source: str | int | None = None
    profile: Dict[str, Any] = Field(default_factory=dict)
    cognitive_profile: EeyoreCognitiveProfile | Dict[str, Any] = Field(
        default_factory=dict,
        alias="cognitive profile",
    )
