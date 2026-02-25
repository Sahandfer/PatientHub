# coding=utf-8
# Licensed under the MIT License;

from .base import BaseClient
from omegaconf import DictConfig
from dataclasses import dataclass


@dataclass
class UserClientConfig:
    """Configuration for UserClient (human user as client)."""

    agent_type: str = "user"
    lang: str = "en"


class UserClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.name = "Human Client"

    def build_sys_prompt(self):
        pass

    def generate_response(self, msg: str):
        res = input("Your response: ")
        return res

    def reset(self):
        self.therapist = None
