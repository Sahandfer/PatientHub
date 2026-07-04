from typing import Literal

from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class MindVoyagerSource(BaseModel):
    dataset: str
    source_profile_id: str


class InternalCognitiveDiagram(BaseModel):
    relevant_history: str = Field(...)
    core_beliefs: list[str] = Field(default_factory=list)
    intermediate_beliefs: list[str] = Field(default_factory=list)
    coping_strategies: str = Field(...)


class ExternalExperience(BaseModel):
    situation: str = Field(...)
    reaction: str = Field(...)
    source: str | None = None


class MindVoyagerCharacter(BaseCharacter):
    id: str = Field(...)
    source: MindVoyagerSource | None = None
    name: str = Field(...)
    style: list[str] = Field(default_factory=list)
    internal_cognitive_diagram: InternalCognitiveDiagram = Field(...)
    external_experiences: list[ExternalExperience] = Field(min_length=1)


class MindVoyagerDifficultyPreset(BaseModel):
    openness: Literal["low", "high"] = Field(...)
    metacognition: Literal["low", "high"] = Field(...)
    initial_visible_external_count: int = Field(ge=0)
    low_metacognition_question_check_interval: int = Field(ge=0)
    high_metacognition_question_check_interval: int = Field(ge=0)


class OpennessAssessment(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
        description="Numerical rating of the client's current openness and rapport.",
    )
    key_examples: list[str] = Field(
        default_factory=list,
        description="Two recent dialogue examples supporting the rating.",
    )
    progression: str = Field(
        default="",
        description="Analysis of current openness progression.",
    )
    turning_point: str = Field(
        default="",
        description="Notable turning point leading to the current openness level.",
    )


class QuestionFacilitationAssessment(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
        description="Rating of how strongly the therapist question facilitates inner exploration.",
    )
    justification: str = Field(
        default="",
        description="Short justification for the question facilitation rating.",
    )
