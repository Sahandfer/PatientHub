from pydantic import BaseModel, Field


class CriticFeedback(BaseModel):
    realism: int = Field(
        ...,
        description="Realism score of the character on a scale from 1 to 10",
    )
    logical_consistency: int = Field(
        ...,
        description="Logical consistency within different aspects of the character profile on a scale from 1 to 10",
    )
    feedback: str = Field(
        ...,
        description="Feedback on the generated character, including strengths and areas for improvement",
    )
    suggestions: list[str] = Field(
        ...,
        description="Suggestions for improving the character profile, if necessary",
    )
