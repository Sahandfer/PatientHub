# coding=utf-8
# Copyright 2025 PatientHub Authors.

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseTherapist


@dataclass
class UserTherapistConfig:
    """Configuration for UserTherapist (human user as therapist)."""

    agent_type: str = "user"
    lang: str = "en"


class UserTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        self.name = "Human Therapist"

    def build_sys_prompt(self):
        pass

    def generate_response(self, msg: str):
        res = input("Your response: ")
        return res

    def reset(self):
        self.client = None
