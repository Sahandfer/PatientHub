from agents import BaseAgent
from typing import Literal
from pydantic import BaseModel, Field
from utils import load_prompts
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class StudentDemographics(BaseModel):
    name: str = Field(..., description="Character's name")
    age: int = Field(..., description="Character's age")
    gender: Literal["male", "female"] = Field(..., description="Character's gender")
    education: str = Field(..., description="Character's major and year of study")
    marital_status: Literal["single", "married"] = Field(
        ..., description="Character's marital status"
    )


class StudentPersonality(BaseModel):
    extraversion: int = Field(
        ..., description="Extraversion score on a scale from 1 to 10"
    )
    agreeableness: int = Field(
        ..., description="Agreeableness score on a scale from 1 to 10"
    )
    conscientiousness: int = Field(
        ..., description="Conscientiousness score on a scale from 1 to 10"
    )
    neuroticism: int = Field(
        ..., description="Neuroticism score on a scale from 1 to 10"
    )
    openness: int = Field(..., description="Openness score on a scale from 1 to 10")


class StudentCurrentIssue(BaseModel):
    Description: str = Field(
        ...,
        description="A short description of the current issue or problem (< 100 words)",
    )
    duration: str = Field(
        ..., description="Duration for which the character has been facing this issue"
    )
    severity: Literal["mild", "moderate", "severe"] = Field(
        ..., description="Severity of the issue"
    )
    impact: str = Field(..., description="Impact of the issue on the character's life")
    coping_strategies: list[str] = Field(
        ...,
        description="Coping strategies the character has tried or is using to deal with the issue -> 2 healthy (e.g., working out or meditation) and 2 unhealthy (e.g., smoking or drinking)",
    )


# Behavior model based on BASK-R framework
# class StudentBehavior(BaseModel):


class StudentClientProfile(BaseModel):
    demographics: StudentDemographics = Field(
        ..., description="Demographic information of the character"
    )
    personality: StudentPersonality = Field(
        ..., description="Personality traits and attributes of the character"
    )
    current_issue: StudentCurrentIssue = Field(
        ..., description="Current issue the character is facing"
    )


class StudentClientGenerator(BaseAgent):
    def __init__(self, model_client: BaseChatModel, api_type: str, data=None):
        self.data = data
        self.model_client = model_client
        self.prompt = (
            "Create a student client profile based on the output requirements."
        )

    def save_characters(self, file_path="characters.json"):
        pass

    def create_characters(self):
        pass

    def generate(self):
        model_client = self.model_client.with_structured_output(StudentClientProfile)
        res = model_client.invoke(SystemMessage(content=self.prompt))
        return res

    def reset(self):
        pass
