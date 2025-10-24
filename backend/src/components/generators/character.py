import json
from typing import Literal
from pydantic import BaseModel, Field
from src.prompts import get_prompt
from src.utils import parse_json_response, get_model_client
from camel.agents import ChatAgent


class Demographics(BaseModel):
    name: str = Field(..., description="Character's name")
    age: Literal["<20", "20s", "30s", "40s", "50+"] = Field(
        ..., description="Character's age"
    )
    gender: Literal["male", "female"] = Field(..., description="Character's gender")
    ethnicity: Literal["white", "black", "hispanic", "asian", "other"] = Field(
        ..., description="Character's ethnicity"
    )
    education: Literal["high_school", "undergraduate", "postgraduate", "other"] = Field(
        ..., description="Character's education level"
    )
    work_status: Literal["student", "employed", "unemployed", "retired", "other"] = (
        Field(..., description="Character's occupation status")
    )
    income: Literal["low", "medium", "high"] = Field(
        ..., description="Character's income level"
    )
    marital_status: Literal["single", "married", "divorced", "widowed", "other"] = (
        Field(..., description="Character's marital status")
    )
    religion: Literal[
        "christianity", "islam", "hinduism", "buddhism", "none", "other"
    ] = Field(..., description="Character's religion")
    children: int = Field(..., description="Number of children the character has")
    living_situation: Literal[
        "alone", "with_family", "with_roommates", "with_partner", "other"
    ] = Field(..., description="Character's living situation")


class Personality(BaseModel):
    traits: list[str] = Field(
        ...,
        description="List of personality traits that describe the character",
    )
    strengths: list[str] = Field(
        ...,
        description="List of character's strengths or positive attributes",
    )
    weaknesses: list[str] = Field(
        ...,
        description="List of character's weaknesses or negative attributes",
    )
    hobbies: list[str] = Field(
        ...,
        description="List of hobbies or interests the character enjoys",
    )
    # goals: list[str] = Field(
    #     ...,
    #     description="List of personal or professional goals the character is pursuing",
    # )


class CurrentIssue(BaseModel):
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


class ClientProfile(BaseModel):
    demographics: Demographics = Field(
        ..., description="Demographic information of the character"
    )
    personality: Personality = Field(
        ..., description="Personality traits and attributes of the character"
    )
    current_issue: CurrentIssue = Field(
        ..., description="Current issue the character is facing"
    )


class TherapistProfile(BaseModel):
    demographics: Demographics = Field(
        ..., description="Demographic information of the character"
    )
    personality: Personality = Field(
        ..., description="Personality traits and attributes of the character"
    )


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


class CharacterGenerator:
    def __init__(self, model_name: str, api_type: str, data=None):
        self.data = data
        self.model_client = get_model_client(model_name, api_type)
        self.generator = self.create_agent(mode="generator")
        self.critic = self.create_agent(mode="critic")
        self.characters = []

    def create_agent(self, mode: str):
        if mode == "generator":
            self.sys_prompt = get_prompt(mode, "client").render(data=self.data)
        elif mode == "critic":
            self.sys_prompt = get_prompt(mode, "character").render(data=self.data)
        return ChatAgent(system_message=self.sys_prompt, model=self.model_client)

    def generate_character(self):
        res = self.generator.step(
            "Generate an output based on the required format",
            response_format=ClientProfile,
        )
        return parse_json_response(res.msgs[0].content)

    def evaluate_character(self, character):
        res = self.generator.step(
            "Evaluate the character based on realism and logical consistency",
            response_format=CriticFeedback,
        )
        return parse_json_response(res.msgs[0].content)

    def save_characters(self, file_path="characters.json"):
        with open(file_path, "w") as f:
            json.dump(self.characters, f, indent=4, ensure_ascii=False)
        print(f"Character saved to {file_path}")

    def create_characters(self):
        # self.create_prompt()
        # self.generate(prompt)
        character = self.generate_character()
        eval_res = self.evaluate_character(character)
        character["critic_feedback"] = eval_res
        self.characters.append(character)
        self.save_characters()


if __name__ == "__main__":
    api_type = "OR"
    model_name = "qwen/qwen3-235b-a22b:free"
    character_generator = CharacterGenerator(model_name=model_name, api_type=api_type)
    character_generator.create_characters()
