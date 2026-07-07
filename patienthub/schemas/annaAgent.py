from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter, ConvTurn


class Profile(BaseModel):
    drisk: int = Field(...)
    srisk: int = Field(...)
    age: str = Field(...)
    gender: str = Field(...)
    marital_status: str = Field(...)
    occupation: str = Field(...)
    symptoms: str = Field(...)


class ComplaintNode(BaseModel):
    stage: int
    content: str


class Report(BaseModel):
    case_title: str = Field(...)
    case_categories: list[str] = Field(...)
    techniques_used: list[str] = Field(...)
    case_summary: list[str] = Field(...)
    counseling_process: list[str] = Field(...)
    insights_and_reflections: list[str] = Field(...)


class Message(BaseModel):
    role: str
    content: str


class AnnaAgentCharacter(BaseCharacter):
    profile: Profile = Field(...)
    situation: str = Field(...)
    status: str = Field(...)
    statement: list[str] = Field(...)
    style: list[str] = Field(...)
    complaint_chain: list[ComplaintNode] = Field(...)
    report: Report = Field(...)
    previous_conversations: list[Message] = Field(default_factory=list)


class AnnaAgentSeed:
    profile: dict
    report: dict | str = ""
    previous_conversations: list[ConvTurn] = Field(default_factory=list)
