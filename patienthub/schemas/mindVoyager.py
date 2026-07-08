from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter

DIFFICULTY_PRESETS = {
    "easy": {
        "openness": "high",
        "metacognition": "high",
        "visible_external_count": 3,
        "low_metacognition_question_check_interval": 2,
        "high_metacognition_question_check_interval": 1,
    },
    "normal": {
        "openness": "high",
        "metacognition": "low",
        "visible_external_count": 2,
        "low_metacognition_question_check_interval": 2,
        "high_metacognition_question_check_interval": 1,
    },
    "hard": {
        "openness": "low",
        "metacognition": "low",
        "visible_external_count": 1,
        "low_metacognition_question_check_interval": 2,
        "high_metacognition_question_check_interval": 1,
    },
    "custom": {
        "openness": "low",
        "metacognition": "high",
        "visible_external_count": 2,
        "low_metacognition_question_check_interval": 2,
        "high_metacognition_question_check_interval": 1,
    },
}

INTERNAL_REVEAL_ORDER = [
    "relevant_history",
    "core_beliefs",
    "intermediate_beliefs",
    "coping_strategies",
]

# Based on the paper
CONSTANTS = {
    "rapport_interval": 4,
    "rapport_threshold": 4,
    "question_threshold": 4,
}


class InternalCognitiveDiagram(BaseModel):
    relevant_history: str = Field(...)
    core_beliefs: list[str] = Field(default_factory=list)
    intermediate_beliefs: list[str] = Field(default_factory=list)
    coping_strategies: str = Field(...)


class ExternalExperience(BaseModel):
    situation: str = Field(...)
    reaction: str = Field(...)


class MindVoyagerCharacter(BaseCharacter):
    source: str | None = None
    name: str = Field(...)
    internal_cognitive_diagram: InternalCognitiveDiagram = Field(...)
    external_experiences: list[ExternalExperience] = Field(min_length=1)


class OpennessAssessment(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
        description="Numerical rating of the client's current openness and rapport.",
    )
    key_examples: list[str] = Field(
        default_factory=list,
        description="Two recent dialogue examples supporting the rating.",
        examples=[
            [
                "Recent quote showing the client's current emotional state.",
                "Latest exchange demonstrating the client's openness.",
            ]
        ],
    )
    progression: str = Field(
        default="",
        description="Analysis of current openness progression.",
        examples=[
            "The client's most recent interactions show more open emotional expression, "
            "a marked change from the guarded tone earlier in the session."
        ],
    )
    turning_point: str = Field(
        default="",
        description="Notable turning point leading to the current openness level.",
        examples=[
            "The client's emotional depth shifted when they began expressing hurt "
            "about their mother's criticism."
        ],
    )


class QuestionFacilitationAssessment(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
        description="Rating of how strongly the therapist question facilitates inner exploration.",
        examples=[3],
    )
    justification: str = Field(
        default="",
        description="Short justification for the question facilitation rating.",
        examples=[
            "The therapist's open-ended question pushed the client to examine the root "
            "of their avoidance rather than restating the facts."
        ],
    )
