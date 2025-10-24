import json
from typing import Literal
from pydantic import BaseModel, Field
from src.prompts import get_prompt
from src.utils import parse_json_response, get_model_client
from camel.agents import ChatAgent


class Event(BaseModel):
    name: str = Field(..., description="Name of the event")
    location: str = Field(..., description="Location of the event")
    description: str = Field(..., description="Brief description of the event")


class BetweenSessionEvents(BaseModel):
    events: list[Event] = Field(
        ...,
        description="List of events that occurred between sessions",
    )


class EventGenerator:
    def __init__(self, model_name: str, api_type: str, data=None):
        self.model_client = get_model_client(model_name, api_type)
        self.agent = self.create_agent()
