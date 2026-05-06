from typing import Literal
from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class IdentifyingData(BaseModel):
    age: str = Field(..., alias="Age")
    sex: str = Field(..., alias="Sex")
    marital_status: Literal["Single", "Married", "Divorced", "Widowed"] = Field(
        ..., alias="Marital status"
    )
    occupation: str = Field(..., alias="Occupation")


class ChiefComplaint(BaseModel):
    description: str = Field(..., alias="Description")


class PresentIllnessSymptom(BaseModel):
    name: str = Field(..., alias="Name")
    length: str | int = Field(..., alias="Length")
    alleviating_factor: str = Field(..., alias="Alleviating factor")
    exacerbating_factor: str = Field(..., alias="Exacerbating factor")
    triggering_factor: str = Field(..., alias="Triggering factor")
    stressor: Literal[
        "work",
        "home",
        "school",
        "legal issue",
        "medical comorbidity",
        "interpersonal difficulty",
        "none",
    ] = Field(..., alias="Stressor")


class PresentIllness(BaseModel):
    symptom: PresentIllnessSymptom = Field(..., alias="Symptom")


class PastPsychiatricHistory(BaseModel):
    presence: str = Field(..., alias="Presence")
    description: str | None = Field(default=None, alias="Description")


class PastMedicalHistory(BaseModel):
    presence: str = Field(..., alias="Presence")
    history: str = Field(..., alias="History")


class CurrentMedication(BaseModel):
    medication_name: str = Field(..., alias="Medication name")
    duration: str = Field(..., alias="Duration")
    compliance: str = Field(..., alias="Compliance")
    effect: str = Field(..., alias="Effect")
    side_effect: str = Field(..., alias="Side effect")


class FamilyHistory(BaseModel):
    diagnosis: str = Field(..., alias="Diagnosis")
    substance_use: str = Field(..., alias="Substance use")


class ChildhoodHistory(BaseModel):
    home_environment: str = Field(..., alias="Home environment")
    members_of_family: str = Field(..., alias="Members of family")
    social_environment: str = Field(..., alias="Social environment")


class DevelopmentalSocialHistory(BaseModel):
    childhood_history: ChildhoodHistory = Field(..., alias="Childhood history")
    school_history: str = Field(..., alias="School history")
    work_history: str = Field(..., alias="Work history")


class Impulsivity(BaseModel):
    suicidal_ideation: Literal["High", "Moderate", "Low"] = Field(
        ..., alias="Suicidal ideation"
    )
    suicidal_plan: Literal["Presence", "Absence"] = Field(..., alias="Suicidal plan")
    suicidal_attempt: Literal["Presence", "Absence"] = Field(
        ..., alias="Suicidal attempt"
    )
    self_mutilating_behavior_risk: Literal["High", "Moderate", "Low"] = Field(
        ..., alias="Self-mutilating behavior risk"
    )
    homicide_risk: Literal["High", "Moderate", "Low"] = Field(
        ..., alias="Homicide risk"
    )


class MFCProfile(BaseModel):
    identifying_data: IdentifyingData = Field(..., alias="Identifying data")
    chief_complaint: ChiefComplaint = Field(..., alias="Chief complaint")
    present_illness: PresentIllness = Field(..., alias="Present illness")
    past_psychiatric_history: PastPsychiatricHistory = Field(
        ..., alias="Past psychiatric history"
    )
    past_medical_history: PastMedicalHistory = Field(..., alias="Past medical history")
    current_medication: CurrentMedication = Field(..., alias="Current medication")
    family_history: FamilyHistory = Field(..., alias="Family history")
    developmental_social_history: DevelopmentalSocialHistory = Field(
        ..., alias="Developmental/social history"
    )
    impulsivity: Impulsivity = Field(..., alias="Impulsivity")


class MFCBehavior(BaseModel):
    general_appearance_attitude_behavior: str = Field(
        ..., alias="General appearance/attitude/behavior"
    )
    mood: str = Field(..., alias="Mood")
    affect: str = Field(..., alias="Affect")
    spontaneity: str = Field(..., alias="Spontaneity")
    verbal_productivity: Literal["Decreased", "Normal", "Increased"] = Field(
        ..., alias="Verbal productivity"
    )
    tone_of_voice: str = Field(..., alias="Tone of voice")
    social_judgement: str = Field(..., alias="Social judgement")
    insight: str = Field(..., alias="Insight")
    reliability: str = Field(..., alias="Reliability")
    perception: str = Field(..., alias="Perception")
    thought_process: str = Field(..., alias="Thought process")
    thought_content: str = Field(..., alias="Thought content")


class PsycheCharacter(BaseCharacter):
    mfc_profile: MFCProfile = Field(..., alias="MFC-Profile")
    mfc_history: str = Field(..., alias="MFC-History")
    mfc_behavior: MFCBehavior = Field(..., alias="MFC-Behavior")

