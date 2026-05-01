from typing import Dict
from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class Persona(BaseModel):
    age: int = Field(...)
    gender: str = Field(...)
    ethnicity: str = Field(...)
    occupation: str = Field(...)
    mbti: str = Field(...)


class SimPatientCharacter(BaseCharacter):
    persona: Persona = Field(...)
    cognitive_model: Dict[str, int] = Field(...)
    between_session_event: str = Field(default="")
