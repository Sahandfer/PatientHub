# coding=utf-8
# Licensed under the MIT License;

from .base import BaseClient
from omegaconf import DictConfig
from dataclasses import dataclass


@dataclass
class UserClientConfig:
    """Configuration for UserClient (human user as client)."""

    agent_name: str = "user"
    lang: str = "en"


class UserClient(BaseClient):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def build_sys_prompt(self):
        pass

    def generate_response(self, msg: str):
        res = input("Your response: ")
        return res
