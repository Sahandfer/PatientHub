from typing import Literal
from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


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
    previous_conversations: list[Message] = Field(...)


# GoEmotions taxonomy constants
EMOTION_TYPES = Literal[
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
]

EMOTION_CATEGORIES = {
    "Positive": [
        "admiration",
        "amusement",
        "approval",
        "caring",
        "curiosity",
        "desire",
        "excitement",
        "gratitude",
        "joy",
        "love",
        "optimism",
        "pride",
        "realization",
        "relief",
        "surprise",
    ],
    "Neutral": ["neutral"],
    "Ambiguous": ["confusion", "disappointment", "nervousness"],
    "Negative": [
        "anger",
        "annoyance",
        "disapproval",
        "disgust",
        "embarrassment",
        "fear",
        "sadness",
        "remorse",
        "grief",
    ],
}

CATEGORY_DISTANCES = {
    "Positive": {"Positive": 0, "Neutral": 1, "Ambiguous": 2, "Negative": 3},
    "Neutral": {"Positive": 1, "Neutral": 0, "Ambiguous": 1, "Negative": 2},
    "Ambiguous": {"Positive": 2, "Neutral": 1, "Ambiguous": 0, "Negative": 1},
    "Negative": {"Positive": 3, "Neutral": 2, "Ambiguous": 1, "Negative": 0},
}

DISTANCE_WEIGHTS = {0: 10, 1: 5, 2: 2, 3: 1}
