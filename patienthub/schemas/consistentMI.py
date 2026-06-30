from typing import Literal
from pydantic import Field

from patienthub.schemas.base import BaseCharacter


STAGES = ["Precontemplation", "Contemplation", "Preparation", "Action", "Maintenance"]


class ConsistentMICharacter(BaseCharacter):
    topic: str = Field(...)
    initial_stage: Literal[*STAGES] = Field(default="Precontemplation")
    suggestibilities: list[int] = Field(...)
    Personas: list[str] = Field(...)
    Acceptable_Plans: list[str] = Field(..., alias="Acceptable Plans")
    Beliefs: list[str] = Field(...)
    Motivation: list[str] = Field(...)
    Behavior: str = Field(...)
