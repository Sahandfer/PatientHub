# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for consistentMI characters."""

from typing import Literal

from pydantic import Field

from .base import CharacterModel


class ConsistentMICharacter(CharacterModel):
    idx: int | None = None
    name: str = "ConsistentMI"
    topic: str
    initial_stage: Literal["Precontemplation", "Contemplation", "Preparation"] = (
        "Precontemplation"
    )
    suggestibilities: list[int] = Field(default_factory=list)
    Personas: list[str] = Field(default_factory=list)
    Acceptable_Plans: list[str] = Field(default_factory=list, alias="Acceptable Plans")
    Beliefs: list[str] = Field(default_factory=list)
    quality: str | None = None
    Motivation: list[str] = Field(default_factory=list)
    Behavior: str = ""
