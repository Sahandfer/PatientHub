import json
from typing import Literal
from pydantic import BaseModel, Field
from patienthub.prompts import get_prompt
from patienthubienthub.utils import parse_json_response, get_chat_model


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
    def __init__(self, model_name: str, model_type: str, data=None):
        self.chat_model = get_chat_model(model_name, model_type)
        self.agent = self.create_agent()
