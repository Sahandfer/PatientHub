from typing import Dict, List
from pydantic import BaseModel, Field

from src.agents import UserAgent

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage


class Response(BaseModel):
    content: str = Field(description="The content of user input")


class UserClient(UserAgent):
    def __init__(self, configs: DictConfig):
        self.name = "client"
        self.messages = []

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "therapist")

    def generate(self, response_format: BaseModel):
        res = input("Your response: ")
        return response_format(content=res)

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(response_format=Response)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.messages = []
        self.therapist = None
