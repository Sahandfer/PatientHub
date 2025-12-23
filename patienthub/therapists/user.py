from dataclasses import dataclass
from patienthub.base import ChatAgent
from omegaconf import DictConfig
from pydantic import BaseModel, Field


@dataclass
class UserTherapistConfig:
    """Configuration for User (human) therapist."""

    agent_type: str = "user"
    lang: str = "en"


class Response(BaseModel):
    content: str = Field(description="The content of user input")


class UserTherapist(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.name = "humanTherapist"

    def set_client(self, client):
        self.client = client.get("name", "client")

    def generate(self):
        res = input("Therapist response: ")
        return Response(content=res.strip())

    def generate_response(self, msg: str):
        res = self.generate()
        return res

    def reset(self):
        self.client = None
