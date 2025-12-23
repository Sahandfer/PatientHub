from dataclasses import dataclass
from patienthub.base import ChatAgent
from omegaconf import DictConfig
from pydantic import BaseModel, Field


@dataclass
class UserClientConfig:
    """Configuration for User (human) client."""

    agent_type: str = "user"


class Response(BaseModel):
    content: str = Field(description="The content of user input")


class UserClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.name = "humanClient"

    def set_therapist(self, therapist):
        self.therapist = therapist.get("name", "therapist")

    def generate(self):
        res = input("Your response: ")
        return Response(content=res.strip())

    def generate_response(self, msg: str):
        res = self.generate()
        return res

    def reset(self):
        self.therapist = None
