from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from patienthub.schemas.base import BaseCharacter


SeverityLevel = Literal["mild", "moderate", "severe"]
AgeStrata = Literal["Child", "Adult", "Elderly"]
BiologicalSex = Literal["Male", "Female"]
PhysiologicalStatus = Literal["Pregnant", "Non-pregnant", "Post-menopausal"]
Ethnicity = Literal[
    "Asian", "Caucasian", "African American", "Hispanic", "Mixed", "Other"
]
Geography = Literal["Urban (Metropolitan)", "Rural", "Suburban"]
IncomeTier = Literal["Low", "Middle", "High"]
Smoking = Literal["Never", "Former", "Current"]
Alcohol = Literal["None", "Moderate", "Heavy"]
DietaryPattern = Literal["Balanced", "High-fat", "High-salt"]
ActivityLevel = Literal["Sedentary", "Moderate", "Active"]
CommunicationStyle = Literal[
    "Plain", "Upset", "Verbose", "Reserved", "Tangent", "Pleasing"
]
MedicinePreference = Literal["Modern", "Traditional"]
ScaleName = Literal["PHQ-9", "GAD-7", "ISI"]
RiskLevel = Literal["none", "low", "moderate", "high"]


class PatientZeroProfileComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PatientZeroPatientProfile(PatientZeroProfileComponent):
    """Background profile B used to ground role-play behavior."""

    age: int = Field(..., ge=0, le=120)
    age_strata: AgeStrata
    biological_sex: BiologicalSex
    physiological_status: PhysiologicalStatus
    ethnicity: Ethnicity
    geography: Geography
    specific_region_constraints: str
    education_level: str
    occupation_type: str
    income_tier: IncomeTier
    smoking: Smoking
    alcohol: Alcohol
    dietary_pattern: DietaryPattern
    activity_level: ActivityLevel
    communication_style: CommunicationStyle
    medicine_preference: MedicinePreference
    name: str
    lifestyle_summary: str
    past_medical_history: str
    family_history: str
    medication_history: str
    allergy_history: str
    vaccination_history: str

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


class PatientZeroSymptom(PatientZeroProfileComponent):
    name: str
    duration: str
    severity: SeverityLevel
    impact: str


class PatientZeroSymptomTrajectory(PatientZeroProfileComponent):
    """Symptom trajectory S that the role-play character should enact."""

    current_severity: SeverityLevel
    chief_complaint: str
    onset: str
    duration: str
    progression: str
    selected_symptoms: list[PatientZeroSymptom]
    associated_symptoms: list[str]
    negative_symptoms: list[str]
    triggers: list[str]
    relieving_factors: list[str]
    functional_impact: str
    risk_features: list[str]


class PatientZeroMentalStatusExam(PatientZeroProfileComponent):
    appearance_behavior: str
    speech: str
    mood_affect: str
    thought_process: str
    thought_content: str
    perception: str
    cognition: str
    insight_judgment: str
    reliability: str


class PatientZeroScaleAssessment(PatientZeroProfileComponent):
    scale_name: ScaleName
    score: int
    severity_interpretation: str
    rationale: str

    @model_validator(mode="after")
    def validate_score_range(self):
        ranges = {"PHQ-9": (0, 27), "GAD-7": (0, 21), "ISI": (0, 28)}
        low, high = ranges[self.scale_name]
        if not low <= self.score <= high:
            raise ValueError(f"{self.scale_name} score must be between {low} and {high}.")
        return self


class PatientZeroRiskAssessment(PatientZeroProfileComponent):
    suicide_risk: RiskLevel
    violence_risk: RiskLevel
    self_neglect_risk: RiskLevel
    rationale: str


class PatientZeroExclusionaryFinding(PatientZeroProfileComponent):
    test_name: str
    finding: str
    interpretation: str


class PatientZeroClinicalEvidence(PatientZeroProfileComponent):
    """Clinical evidence E included in the final role-play profile."""

    mental_status_exam: PatientZeroMentalStatusExam
    scale_assessments: list[PatientZeroScaleAssessment]
    risk_assessment: PatientZeroRiskAssessment
    exclusionary_findings: list[PatientZeroExclusionaryFinding]
    clinical_summary: str


class PatientZeroCharacter(BaseCharacter):
    """Role-play-ready Patient-Zero profile P={B,S,E}."""

    patient_profile: PatientZeroPatientProfile
    symptom_trajectory: PatientZeroSymptomTrajectory
    examination_results: PatientZeroClinicalEvidence


class PatientZeroDataset(RootModel[list[PatientZeroCharacter]]):
    pass


PatientZeroFinalRecord = PatientZeroCharacter
PatientZeroFinalOutput = PatientZeroDataset