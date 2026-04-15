# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for annaAgent characters."""

from pydantic import Field, model_validator

from .base import CharacterModel


class AnnaAgentCharacter(CharacterModel):
    class Profile(CharacterModel):
        drisk: int | str
        srisk: int | str
        age: int | str
        gender: str
        marital_status: str
        occupation: str
        symptoms: str

    class ComplaintNode(CharacterModel):
        stage: int = Field(ge=1)
        content: str

    class Report(CharacterModel):
        case_title: str
        case_categories: list[str] = Field(min_length=1)
        techniques_used: list[str] = Field(min_length=1)
        case_summary: list[str] = Field(min_length=1)
        counseling_process: list[str] = Field(min_length=1)
        insights_and_reflections: list[str] = Field(min_length=1)

    class ConversationTurn(CharacterModel):
        role: str
        content: str

    profile: Profile
    situation: str
    statement: list[str] = Field(min_length=1)
    style: list[str] = Field(min_length=1)
    complaint_chain: list[ComplaintNode] = Field(min_length=3)
    status: str
    report: Report
    previous_conversations: list[ConversationTurn]

    @model_validator(mode="after")
    def validate_complaint_chain(self) -> "AnnaAgentCharacter":
        stages = [node.stage for node in self.complaint_chain]
        expected = list(range(1, len(stages) + 1))
        if stages != expected:
            raise ValueError(
                "complaint_chain stages must be contiguous starting at 1"
            )
        return self
