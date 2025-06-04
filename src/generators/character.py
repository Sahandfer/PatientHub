import os
import json
from typing import Literal
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from src.prompts import get_prompt
from langchain_core.output_parsers import PydanticOutputParser


load_dotenv(".env")

model = ChatOpenAI(
    model=os.environ.get("MODEL_NAME"),
    base_url=os.environ.get("BASE_URL"),
    api_key=os.environ.get("API_KEY"),
    temperature=0.6,
)


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
    occupation: Literal["student", "employed", "unemployed", "retired", "other"] = (
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


def create_prompt(mode="client", data=[]):
    profile = ClientProfile if mode == "client" else None
    parser = PydanticOutputParser(pydantic_object=profile)
    if mode in ["client", "therapist"]:
        output_format = parser.get_format_instructions()
        return get_prompt("generator", "character").render(
            data=data, output_format=output_format, mode=mode
        )
    elif mode == "critic":
        return get_prompt("critic", "character").render(data=data)
    else:
        return None


def generate(prompt):
    messages = [{"role": "system", "content": prompt}]
    res = model.invoke(messages)
    return res.content


def jsonify(data):
    data = data.replace("```json", '"').replace("```", "")
    return json.loads(data)


def save_character(character_data, file_path="characters.json"):
    with open(file_path, "w") as f:
        json.dump(character_data, f, indent=4)
    print(f"Character saved to {file_path}")


if __name__ == "__main__":
    # print(prompt)
    gen_prompt = create_prompt(mode="client", data=[])
    character = generate(prompt=gen_prompt)
    print(character)
    eval_prompt = create_prompt(mode="critic", data=character)
    evaluation = generate(prompt=eval_prompt)
    print(evaluation)
