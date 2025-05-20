from pydantic import BaseModel, Field


class MentalState(BaseModel):
    beliefs: str = Field(description="Current beliefs")
    emotions: str = Field(description="Current emotions")
    desires: str = Field(description="Current desires")
    intents: str = Field(description="Current intents")
