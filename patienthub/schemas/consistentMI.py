from pydantic import Field

from patienthub.schemas.base import BaseCharacter


class ConsistentMICharacter(BaseCharacter):
    topic: str = Field(...)
    initial_stage: str = Field(...)
    suggestibilities: list[int] = Field(...)
    Personas: list[str] = Field(...)
    Acceptable_Plans: list[str] = Field(..., alias="Acceptable Plans")
    Beliefs: list[str] = Field(...)
    Motivation: list[str] = Field(...)
    Behavior: str = Field(...)
