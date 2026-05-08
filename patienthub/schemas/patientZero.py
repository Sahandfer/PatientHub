from typing import Literal
from pydantic import BaseModel, Field, model_validator

from patienthub.schemas.base import BaseCharacter

RISK_LEVEL = Literal["none", "low", "moderate", "high"]


class PatientDemographics(BaseModel):
    """Demographic and lifestyle attributes."""

    age: int = Field(..., ge=0, le=120)
    age_strata: Literal["Child", "Adult", "Elderly"]
    biological_sex: Literal["Male", "Female"]
    physiological_status: Literal["Pregnant", "Non-pregnant", "Post-menopausal"]
    ethnicity: Literal[
        "Asian", "Caucasian", "African American", "Hispanic", "Mixed", "Other"
    ]
    geography: Literal["Urban (Metropolitan)", "Rural", "Suburban"]
    specific_region_constraints: str
    education_level: str
    occupation_type: str
    income_tier: Literal["Low", "Middle", "High"]
    smoking: Literal["Never", "Former", "Current"]
    alcohol: Literal["None", "Moderate", "Heavy"]
    dietary_pattern: Literal["Balanced", "High-fat", "High-salt"]
    activity_level: Literal["Sedentary", "Moderate", "Active"]
    communication_style: Literal[
        "Plain", "Upset", "Verbose", "Reserved", "Tangent", "Pleasing"
    ]
    medicine_preference: Literal["Modern", "Traditional"]

    @model_validator(mode="after")
    def validate_constraints(self):
        if (
            self.biological_sex == "Male"
            and self.physiological_status != "Non-pregnant"
        ):
            raise ValueError("Male patients cannot be pregnant or post-menopausal.")
        if self.age_strata == "Child" and self.physiological_status != "Non-pregnant":
            raise ValueError("Child patients cannot be pregnant or post-menopausal.")
        if self.age_strata == "Elderly" and self.physiological_status == "Pregnant":
            raise ValueError("Elderly patients cannot be pregnant.")
        return self


class PatientNarrative(BaseModel):
    """LLM-generated narrative fields."""

    name: str
    lifestyle_summary: str
    past_medical_history: str
    family_history: str
    medication_history: str
    allergy_history: str
    vaccination_history: str


class PatientZeroPatientProfile(PatientDemographics, PatientNarrative):
    """Background profile B used to ground role-play behavior."""


class SymptomEntry(BaseModel):

    name: str
    duration: str
    severity: Literal["mild", "moderate", "severe"]
    impact: str


class SymptomTrajectory(BaseModel):
    """Symptom trajectory S that the role-play character should enact."""

    current_severity: Literal["mild", "moderate", "severe"]
    chief_complaint: str
    onset: str
    duration: str
    progression: str
    selected_symptoms: list[SymptomEntry]
    associated_symptoms: list[str]
    negative_symptoms: list[str]
    triggers: list[str]
    relieving_factors: list[str]
    functional_impact: str
    risk_features: list[str]


class MentalStatusExam(BaseModel):

    appearance_behavior: str
    speech: str
    mood_affect: str
    thought_process: str
    thought_content: str
    perception: str
    cognition: str
    insight_judgment: str
    reliability: str


class ScaleAssessment(BaseModel):

    scale_name: Literal["PHQ-9", "GAD-7", "ISI"]
    score: int
    severity_interpretation: str
    rationale: str

    @model_validator(mode="after")
    def validate_score_range(self):
        ranges = {"PHQ-9": (0, 27), "GAD-7": (0, 21), "ISI": (0, 28)}
        low, high = ranges[self.scale_name]
        if not low <= self.score <= high:
            raise ValueError(
                f"{self.scale_name} score must be between {low} and {high}."
            )
        return self


class RiskAssessment(BaseModel):
    suicide_risk: RISK_LEVEL
    violence_risk: RISK_LEVEL
    self_neglect_risk: RISK_LEVEL
    rationale: str


class ExclusionaryFinding(BaseModel):
    test_name: str
    finding: str
    interpretation: str


class ExaminationResults(BaseModel):
    """Clinical evidence E included in the final role-play profile."""

    mental_status_exam: MentalStatusExam
    scale_assessments: list[ScaleAssessment]
    risk_assessment: RiskAssessment
    exclusionary_findings: list[ExclusionaryFinding]
    clinical_summary: str


class PatientZeroCharacter(BaseCharacter):
    """Role-play-ready Patient-Zero profile P={B,S,E}."""

    patient_profile: PatientZeroPatientProfile
    symptom_trajectory: SymptomTrajectory
    examination_results: ExaminationResults
