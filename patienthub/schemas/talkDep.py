from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class Symptom(BaseModel):
    name: str
    description: str
    severity: int


class TalkDepCharacter(BaseCharacter):
    name: str = Field(...)
    age: int = Field(...)
    gender: str = Field(...)
    bdi_score: int = Field(...)
    depression_level: str = Field(...)
    key_negative_symptoms: list[Symptom] | None = Field(..., default_factory=list)
    life_history: list[str] = Field(...)
    social_context: list[str] = Field(...)
    past_interactions: list[str] = Field(...)
    linguistic_patterns: list[str] = Field(...)
    emotional_tone: list[str] = Field(...)
    typical_topics: list[str] = Field(...)
    behavioral_constraints: list[str] = Field(...)
    response_goals: list[str] = Field(...)
    social_media_activity: list[str] = Field(...)
    current_context_of_interaction: list[str] = Field(...)
