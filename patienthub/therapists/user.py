from omegaconf import DictConfig
from dataclasses import dataclass
from patienthub.base import ChatAgent


@dataclass
class UserTherapistConfig:
    """Configuration for UserTherapist (human user as therapist)."""

    agent_type: str = "user"
    lang: str = "en"


class UserTherapist(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.name = "Human Therapist"

    def set_client(self, client):
        self.client = client.get("name", "client")

    def generate_response(self, msg: str):
        res = input("Your response: ")
        return res

    def reset(self):
        self.client = None
