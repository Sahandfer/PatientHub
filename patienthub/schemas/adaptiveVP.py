from pydantic import Field

from patienthub.schemas.base import BaseCharacter


class AdaptiveVPCharacter(BaseCharacter):
    type_text: str = Field(..., alias="type-text")
    name: str = Field(...)
    situation: str = Field(...)
    chief_complaint: str = Field(..., alias="Chief complaint")
    gender: str = Field(...)
    age: int = Field(...)
    religion: str = Field(...)
    height: str = Field(...)
    weight: str = Field(...)
    main_symptom: str = Field(..., alias="Main symptom")
    history_of_present_illness: str = Field(
        ...,
        alias="History of present illness",
    )
    social_history: str = Field(..., alias="social history")
    past_medical_history: str = Field(..., alias="past medical history")
    past_surgical_history_and_date: str = Field(
        ...,
        alias="past surgical history & date",
    )
    family_medical_history: str = Field(..., alias="family medical history")
    allergies: str = Field(...)
    immunization: str = Field(...)
    medication: str = Field(...)
    primary_diagnosis: str = Field(..., alias="primary diagnosis")
    communication_summary: str = Field(...)
    first_statement: str = Field(...)
