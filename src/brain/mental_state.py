from pydantic import BaseModel, Field


class MentalState(BaseModel):
    Emotion: str = Field(
        description="Current emotion based on Ekman's 8 emotions (label only)",
        default="Unknown",
    )
    Beliefs: str = Field(
        description="Current beliefs (1-2 sentences)", default="Unknown"
    )
    Desires: str = Field(
        description="Current desires (1-2 sentences)", default="Unknown"
    )
    Intents: str = Field(
        description="Current intentions (1-2 sentences) ", default="Unknown"
    )
    Trust_Level: int = Field(
        description="Crrent level of trust towards the therapist (0-100)",
        default=0,
    )
