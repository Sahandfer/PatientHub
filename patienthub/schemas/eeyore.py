from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class Profile(BaseModel):
    model_config = {"populate_by_name": True}

    name: str = Field(...)
    gender: str = Field(...)
    age: str = Field(...)
    marital_status: str = Field(..., alias="marital status")
    occupation: str = Field(...)
    situation: str = Field(..., alias="situation of the client")
    resistance: str = Field(..., alias="resistance toward the support")
    symptom_severity: dict = Field(..., alias="symptom severity")
    cognition_distortion: dict = Field(..., alias="cognition distortion exhibition")
    depression_severity: str = Field(..., alias="depression severity")
    suicidal_ideation_severity: str = Field(..., alias="suicidal ideation severity")
    homicidal_ideation_severity: str = Field(..., alias="homicidal ideation severity")
    counseling_history: str = Field(..., alias="counseling history")


class EeyoreCharacter(BaseCharacter):
    profile: Profile = Field(...)
