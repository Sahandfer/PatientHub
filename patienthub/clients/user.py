from omegaconf import DictConfig
from dataclasses import dataclass
from patienthub.base import ChatAgent


@dataclass
class UserClientConfig:
    """Configuration for UserClient (human user as client)."""

    agent_type: str = "user"
    lang: str = "en"


class UserClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.name = "Human Client"

    def set_therapist(self, therapist):
        self.therapist = therapist.get("name", "therapist")

    def generate_response(self, msg: str):
        res = input("Your response: ")
        return res

    def reset(self):
        self.therapist = None
