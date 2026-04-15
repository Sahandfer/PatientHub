# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for patientPsi characters."""

from pydantic import Field

from .base import CharacterModel


class PatientPsiCharacter(CharacterModel):
    name: str
    id: str | int | None = None
    type: list[str] | str | int | None = None
    history: str = ""
    helpless_belief: list[str] | str = Field(default_factory=list)
    unlovable_belief: list[str] | str = Field(default_factory=list)
    worthless_belief: list[str] | str = Field(default_factory=list)
    intermediate_belief: str = ""
    intermediate_belief_depression: str = ""
    coping_strategies: str = ""
    situation: str = ""
    auto_thought: list[str] | str = Field(default_factory=list)
    emotion: list[str] | str = Field(default_factory=list)
    behavior: list[str] | str = Field(default_factory=list)
