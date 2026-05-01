from typing import Literal
from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class BasicProfile(BaseModel):
    name: str = Field(
        ...,
        description="Client's name; use 'Not Specified' if it cannot be identified.",
    )
    gender: Literal["Male", "Female", "Cannot be identified"] = Field(
        ..., description="Most probable gender of the client based on the conversation."
    )
    age: int = Field(
        ...,
        description="Estimated age of the client; use -1 if age cannot be reasonably inferred.",
    )
    age_explain: str = Field(
        ...,
        description="Brief explanation for the estimated age or 'unclear' if it cannot be inferred.",
    )
    occupation: str = Field(
        ...,
        description="Client's occupation; use 'Not Specified'/'unclear' when appropriate.",
    )
    topic: str = Field(
        ...,
        description="Main topic of the conversation (e.g. 'smoking cessation') followed by a short explanation.",
    )
    situation: str = Field(
        ...,
        description="One-sentence summary of the client's current situation and mental health.",
    )
    emotion: str = Field(
        ..., description="One-sentence summary of the client's feelings and emotions."
    )
    reasons: str = Field(
        ...,
        description="Reasons for the client's visit, starting with 'The client is visiting the therapist because'.",
    )
    problem: str = Field(
        ...,
        description="Main problem the client is facing, starting with problem type followed by a short explanation.",
    )
    emotion_trigger: str = Field(
        ...,
        description="Therapist behaviors that elicited an emotional reaction, with direct quotations, or 'No emotional trigger'.",
    )
    feeling_expression: str = Field(
        ...,
        description="Level of unwillingness to express feelings: 'Low', 'Medium', 'High', or 'Cannot be identified', with a one-sentence explanation.",
    )
    emotional_fluctuation: str = Field(
        ...,
        description="Frequency of emotional fluctuations: 'Low', 'Medium', 'High', or 'Cannot be identified', with a one-sentence explanation.",
    )
    resistance: str = Field(
        ...,
        description="Level of resistance toward the therapist: 'Low', 'Medium', 'High', or 'Cannot be identified', with a one-sentence explanation.",
    )


class Trait(BaseModel):
    score_percent: int = Field(
        ...,
        ge=0,
        le=100,
        description="Estimated level of the trait as an integer percentage from 0 to 100.",
    )
    explanation: str = Field(
        ...,
        description="A clear, single-sentence explanation grounded in the conversation.",
    )


class BigFive(BaseModel):
    Openness: Trait = Field(..., description="Openness estimate.")
    Conscientiousness: Trait = Field(..., description="Conscientiousness estimate.")
    Extraversion: Trait = Field(..., description="Extraversion estimate.")
    Agreeableness: Trait = Field(..., description="Agreeableness estimate.")
    Neuroticism: Trait = Field(..., description="Neuroticism estimate.")


class ClientCastCharacter(BaseCharacter):
    basic_profile: BasicProfile = Field(...)
    big_five: BigFive = Field(...)
    symptoms: dict = Field(...)  # PHQ-9/GAD-7/OQ-45 structure varies per item
