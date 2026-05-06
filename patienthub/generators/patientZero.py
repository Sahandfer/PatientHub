# coding=utf-8
# Licensed under the MIT License;

"""Patient-Zero Generator - Creates standardized static patient-record scaffolds."""

import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Literal

from omegaconf import DictConfig
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.utils import get_chat_model, load_json, load_prompts, save_json

@dataclass
class PatientZeroGeneratorConfig(APIModelConfig):
    """Configuration for the Patient-Zero generator."""

    agent_name: str = "patientZero"
    prompt_path: str = "data/prompts/generator/patientZero.yaml"
    source_data_dir: str = "data/resources/PatientZero"
    workspace_dir: str = "data/resources/PatientZero"
    output_path: str = "data/characters/PatientZero.json"
    disease_key: str | None = None
    random_seed: int | None = None

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




class TypicalPresentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mild: str = Field(..., description="Typical mild presentation.")
    moderate: str = Field(..., description="Typical moderate presentation.")
    severe: str = Field(..., description="Typical severe presentation.")


class DiseaseOutline(BaseModel):
    """Standardized disease outline used as Patient-Zero's latent scaffold."""

    model_config = ConfigDict(extra="forbid")

    disease_summary: str = Field(..., description="Brief clinical disease summary.")
    key_characteristics: list[str] = Field(
        ..., description="Core disease characteristics relevant to generation."
    )
    typical_presentation: TypicalPresentation = Field(
        ..., description="Severity-specific presentation anchors."
    )
    important_notes: list[str] = Field(
        ..., description="Generation-relevant clinical notes."
    )
    contraindications: list[str] = Field(
        ..., description="Clinically impossible or inconsistent combinations to avoid."
    )
    differential_considerations: list[str] = Field(
        ..., description="Nearby diagnoses or alternative explanations."
    )
    special_populations: list[str] = Field(
        ..., description="Population-specific considerations and constraints."
    )
    red_flags: list[str] = Field(..., description="Urgent or high-risk features.")


class PatientAttributes(BaseModel):
    """Patient-Zero Stage II sampled patient attribute vector."""

    model_config = ConfigDict(extra="forbid")

    disease_name: str
    severity_level: SeverityLevel
    age_strata: AgeStrata
    age: int = Field(..., ge=0, le=120)
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


class PatientProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    lifestyle_summary: str
    past_medical_history: str
    family_history: str
    medication_history: str
    allergy_history: str
    vaccination_history: str


class SymptomEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    duration: str
    severity: SeverityLevel
    impact: str


class SymptomTrajectory(BaseModel):
    model_config = ConfigDict(extra="forbid")

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


class PatientRecordAndSymptoms(BaseModel):
    """Patient-Zero Stage III LLM output."""

    model_config = ConfigDict(extra="forbid")

    patient_profile: PatientProfile
    symptom_trajectory: SymptomTrajectory


class MentalStatusExam(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

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


class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suicide_risk: RiskLevel
    violence_risk: RiskLevel
    self_neglect_risk: RiskLevel
    rationale: str


class ExclusionaryFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_name: str
    finding: str
    interpretation: str


class ExaminationResults(BaseModel):
    """Patient-Zero Stage IV LLM output."""

    model_config = ConfigDict(extra="forbid")

    mental_status_exam: MentalStatusExam
    scale_assessments: list[ScaleAssessment]
    risk_assessment: RiskAssessment
    exclusionary_findings: list[ExclusionaryFinding]
    clinical_summary: str


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    issues: list[str] = Field(default_factory=list)
    rationale: str
    revision_guidance: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_decision(self):
        if self.passed and self.issues:
            raise ValueError("Passed validation cannot include issues.")
        if not self.passed and not self.issues:
            raise ValueError("Failed validation must include at least one issue.")
        return self


class ClinicalRecordValidation(ValidationResult):
    """Patient-Zero Stage V validation for patient profile and symptoms."""


class ExaminationResultValidation(ValidationResult):
    """Patient-Zero Stage V validation for examination results."""


class PatientZeroGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(self.configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.source_data_dir = Path(self.configs.source_data_dir)
        self.workspace_dir = Path(self.configs.workspace_dir)
        self.raw_outline_path = self.source_data_dir / "raw_outlines.json"
        self.disease_outline_path = self.workspace_dir / "disease_outlines.json"
        self.attribute_priors_path = self.source_data_dir / "attribute_priors.json"
        self.disease_attribute_priors_path = (
            self.source_data_dir / "disease_attribute_priors.json"
        )
        self.exam_reference_path = self.source_data_dir / "exam_references.json"
        self.final_output_path = Path(self.configs.output_path)
        self.disease_key = self.configs.disease_key

    @staticmethod
    def _normalize_key(value: str) -> str:
        return value.strip().lower().replace("-", "_").replace(" ", "_")

    @staticmethod
    def _weighted_choice(distribution: dict[str, float], rng: random.Random) -> str:
        weights = [float(weight) for weight in distribution.values()]
        if sum(weights) <= 0:
            raise ValueError("Weighted distribution must have a positive total.")
        return rng.choices(list(distribution), weights=weights, k=1)[0]

    def _resolve_outline_key(self, disease_key: str) -> str:
        normalized_key = self._normalize_key(disease_key)
        raw_outlines = load_json(str(self.raw_outline_path))
        if normalized_key in raw_outlines:
            return normalized_key
        for key, data in sorted(raw_outlines.items()):
            disease_name = data.get("disease_name", key)
            if normalized_key == self._normalize_key(disease_name):
                return key
        raise ValueError(f"Unknown Patient-Zero disease outline: {disease_key}")

    def _attribute_distributions(self, disease_key: str) -> tuple[dict, dict]:
        priors = load_json(str(self.attribute_priors_path))
        distributions = {
            key: value.copy()
            for key, value in priors["global"].items()
        }
        disease_priors = load_json(str(self.disease_attribute_priors_path))
        overrides = disease_priors.get(self._normalize_key(disease_key), {})
        for key, value in overrides.items():
            distributions[key] = value.copy()
        return distributions, priors["age_ranges"]

    @staticmethod
    def _load_payload(
        payload: dict | list | str | Path,
        seed: int | None = None,
    ) -> dict:
        if isinstance(payload, (str, Path)):
            payload = load_json(str(payload))
        if isinstance(payload, list):
            if not payload:
                raise ValueError("Patient-Zero payload list is empty.")
            if seed is not None:
                for item in reversed(payload):
                    if item.get("metadata", {}).get("seed") == seed:
                        return item
                raise ValueError(f"No Patient-Zero payload found for seed {seed}.")
            return payload[-1]
        if seed is not None and payload.get("metadata", {}).get("seed") != seed:
            raise ValueError(f"No Patient-Zero payload found for seed {seed}.")
        return payload

    def _next_case_index(self, disease_key: str) -> int:
        if not self.final_output_path.exists():
            return 0
        payload = load_json(str(self.final_output_path))
        records = payload if isinstance(payload, list) else [payload]
        return sum(
            1
            for record in records
            if record.get("metadata", {}).get("disease_key") == disease_key
        )

    def _exam_reference(self, disease_key: str) -> dict:
        refs = load_json(str(self.exam_reference_path))
        disease_ref = refs["diseases"].get(self._normalize_key(disease_key), {})
        selected_scales = disease_ref.get("selected_scales", [])
        return {
            "scale_pool": {
                scale: refs["scale_pool"][scale]
                for scale in selected_scales
                if scale in refs["scale_pool"]
            },
            "disease_reference": disease_ref,
        }

    def _with_revision_guidance(
        self,
        prompt: str,
        revision_guidance: list[str] | None = None,
    ) -> str:
        if not revision_guidance:
            return prompt
        guidance = json.dumps(revision_guidance, ensure_ascii=False, indent=2)
        revision_prompt = self.prompts["revision_guidance"].render(
            revision_guidance=guidance
        )
        return f"{prompt}\n\n{revision_prompt}"

    def generate_disease_outline(self, disease_key: str) -> DiseaseOutline:
        """Generate a standardized Stage I disease outline for a disease."""

        outline_key = self._resolve_outline_key(disease_key)
        data = load_json(str(self.raw_outline_path)).get(outline_key)
        raw_outline = data.get("raw_outline", data)
        prompt = self.prompts["disease_outline_generation"].render(
            disease_name=data.get("disease_name", outline_key),
            raw_outline=json.dumps(raw_outline, ensure_ascii=False, indent=2),
        )
        outline = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=DiseaseOutline,
        )
        disease_outlines = (
            load_json(str(self.disease_outline_path))
            if self.disease_outline_path.exists()
            else {}
        )
        disease_outlines[outline_key] = outline.model_dump()
        save_json(
            data=disease_outlines,
            output_dir=str(self.disease_outline_path),
            overwrite=True,
        )
        return outline

    def sample_patient_attributes(
        self,
        disease_key: str,
        severity_level: SeverityLevel | None = None,
        seed: int | None = None,
        max_retries: int = 100,
    ) -> PatientAttributes:
        """Sample a valid Patient-Zero Stage II attribute vector."""

        outline_key = self._resolve_outline_key(disease_key)
        disease_name = load_json(str(self.raw_outline_path)).get(outline_key).get(
            "disease_name", outline_key
        )
        distributions, age_ranges = self._attribute_distributions(outline_key)
        rng = random.Random(seed)

        for _ in range(max_retries):
            age_strata = self._weighted_choice(distributions["age_strata"], rng)
            age_min, age_max = age_ranges[age_strata]
            data = {
                "disease_name": disease_name,
                "severity_level": severity_level
                or self._weighted_choice(distributions["severity_level"], rng),
                "age_strata": age_strata,
                "age": rng.randint(age_min, age_max),
                "biological_sex": self._weighted_choice(
                    distributions["biological_sex"], rng
                ),
                "physiological_status": self._weighted_choice(
                    distributions["physiological_status"], rng
                ),
                "ethnicity": self._weighted_choice(distributions["ethnicity"], rng),
                "geography": self._weighted_choice(distributions["geography"], rng),
                "specific_region_constraints": self._weighted_choice(
                    distributions["specific_region_constraints"], rng
                ),
                "education_level": self._weighted_choice(
                    distributions["education_level"], rng
                ),
                "occupation_type": self._weighted_choice(
                    distributions["occupation_type"], rng
                ),
                "income_tier": self._weighted_choice(distributions["income_tier"], rng),
                "smoking": self._weighted_choice(distributions["smoking"], rng),
                "alcohol": self._weighted_choice(distributions["alcohol"], rng),
                "dietary_pattern": self._weighted_choice(
                    distributions["dietary_pattern"], rng
                ),
                "activity_level": self._weighted_choice(
                    distributions["activity_level"], rng
                ),
                "communication_style": self._weighted_choice(
                    distributions["communication_style"], rng
                ),
                "medicine_preference": self._weighted_choice(
                    distributions["medicine_preference"], rng
                ),
            }
            try:
                return PatientAttributes(**data)
            except ValueError:
                continue

        raise RuntimeError(
            f"Failed to sample a valid Patient-Zero attribute vector for {disease_key}."
        )

    def generate_patient_record_symptoms(
        self,
        disease_key: str,
        attributes: PatientAttributes | dict | None = None,
        seed: int | None = None,
        revision_guidance: list[str] | None = None,
    ) -> dict:
        """Generate Stage III patient profile and symptom trajectory."""

        if attributes is None:
            attributes = self.sample_patient_attributes(disease_key, seed=seed)
        elif isinstance(attributes, dict):
            attributes = PatientAttributes(**attributes)

        outline_key = self._resolve_outline_key(disease_key)
        outline = DiseaseOutline.model_validate(
            load_json(str(self.disease_outline_path)).get(outline_key)
        )
        prompt = self.prompts["patient_record_symptom_generation"].render(
            disease_name=attributes.disease_name,
            severity_level=attributes.severity_level,
            patient_attributes=attributes.model_dump_json(indent=2),
            symptoms_list=json.dumps(
                load_json(str(self.raw_outline_path))
                .get(outline_key)
                .get("raw_outline", {})
                .get("common_symptoms", []),
                ensure_ascii=False,
                indent=2,
            ),
            disease_outline=outline.model_dump_json(indent=2),
        )
        prompt = self._with_revision_guidance(prompt, revision_guidance)
        record = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=PatientRecordAndSymptoms,
        )

        profile = {
            "age": attributes.age,
            "age_strata": attributes.age_strata,
            "biological_sex": attributes.biological_sex,
            "physiological_status": attributes.physiological_status,
            "ethnicity": attributes.ethnicity,
            "geography": attributes.geography,
            "specific_region_constraints": attributes.specific_region_constraints,
            "education_level": attributes.education_level,
            "occupation_type": attributes.occupation_type,
            "income_tier": attributes.income_tier,
            "smoking": attributes.smoking,
            "alcohol": attributes.alcohol,
            "dietary_pattern": attributes.dietary_pattern,
            "activity_level": attributes.activity_level,
            "communication_style": attributes.communication_style,
            "medicine_preference": attributes.medicine_preference,
            **record.patient_profile.model_dump(),
        }
        trajectory = {
            "current_severity": attributes.severity_level,
            **record.symptom_trajectory.model_dump(),
        }
        return {
            "metadata": {
                "disease_name": attributes.disease_name,
                "disease_key": outline_key,
                "severity_level": attributes.severity_level,
                "disease_outline_id": f"{outline_key}.json",
                "seed": seed,
            },
            "sampled_attributes": attributes.model_dump(),
            "patient_profile": profile,
            "symptom_trajectory": trajectory,
        }

    def generate_examination_results(
        self,
        disease_key: str,
        patient_record: dict | None = None,
        seed: int | None = None,
        revision_guidance: list[str] | None = None,
    ) -> dict:
        """Generate Stage IV examination results in one LLM call."""

        if patient_record is None:
            raise RuntimeError(
                "Stage IV cannot be called directly; pass a Stage III patient_record."
            )
        outline_key = self._resolve_outline_key(disease_key)
        patient_record = self._load_payload(patient_record, seed=seed)
        outline = DiseaseOutline.model_validate(
            load_json(str(self.disease_outline_path)).get(outline_key)
        )
        prompt = self.prompts["examination_result_generation"].render(
            disease_name=patient_record["metadata"]["disease_name"],
            severity_level=patient_record["metadata"]["severity_level"],
            patient_record=json.dumps(patient_record, ensure_ascii=False, indent=2),
            disease_outline=outline.model_dump_json(indent=2),
            exam_reference=json.dumps(
                self._exam_reference(outline_key),
                ensure_ascii=False,
                indent=2,
            ),
        )
        prompt = self._with_revision_guidance(prompt, revision_guidance)
        results = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ExaminationResults,
        )

        return {
            **patient_record,
            "examination_results": results.model_dump(),
        }

    def validate_patient_record(
        self,
        patient_record: dict | str | Path,
        disease_key: str,
    ) -> ClinicalRecordValidation:
        """Validate Stage III profile and symptom content."""

        patient_record = self._load_payload(patient_record)
        outline_key = self._resolve_outline_key(disease_key)
        outline = DiseaseOutline.model_validate(
            load_json(str(self.disease_outline_path)).get(outline_key)
        )
        prompt = self.prompts["patient_record_validation"].render(
            disease_name=patient_record["metadata"]["disease_name"],
            severity_level=patient_record["metadata"]["severity_level"],
            patient_attributes=json.dumps(
                patient_record["sampled_attributes"],
                ensure_ascii=False,
                indent=2,
            ),
            generated_record=json.dumps(
                {
                    "patient_profile": patient_record["patient_profile"],
                    "symptom_trajectory": patient_record["symptom_trajectory"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            disease_outline=outline.model_dump_json(indent=2),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ClinicalRecordValidation,
        )

    def validate_examination_results(
        self,
        patient_record: dict | str | Path,
        disease_key: str,
    ) -> ExaminationResultValidation:
        """Validate Stage IV examination results."""

        patient_record = self._load_payload(patient_record)
        outline_key = self._resolve_outline_key(disease_key)
        outline = DiseaseOutline.model_validate(
            load_json(str(self.disease_outline_path)).get(outline_key)
        )
        prompt = self.prompts["examination_result_validation"].render(
            disease_name=patient_record["metadata"]["disease_name"],
            severity_level=patient_record["metadata"]["severity_level"],
            patient_info=json.dumps(
                patient_record["patient_profile"],
                ensure_ascii=False,
                indent=2,
            ),
            symptoms_data=json.dumps(
                patient_record["symptom_trajectory"],
                ensure_ascii=False,
                indent=2,
            ),
            exam_results=json.dumps(
                patient_record["examination_results"],
                ensure_ascii=False,
                indent=2,
            ),
            expected_exams=json.dumps(
                self._exam_reference(outline_key),
                ensure_ascii=False,
                indent=2,
            ),
            disease_outline=outline.model_dump_json(indent=2),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ExaminationResultValidation,
        )

    def generate_static_record(
        self,
        disease_key: str,
        seed: int | None = None,
        max_retries: int = 3,
    ) -> dict:
        """Generate final static Patient-Zero record P={B,S,E} with validation."""

        outline_key = self._resolve_outline_key(disease_key)
        attributes = self.sample_patient_attributes(outline_key, seed=seed)
        record_logs = []
        exam_logs = []
        record_revision_guidance = None
        exam_revision_guidance = None

        for attempt in range(1, max_retries + 1):
            patient_record = self.generate_patient_record_symptoms(
                outline_key,
                attributes=attributes,
                seed=seed,
                revision_guidance=record_revision_guidance,
            )
            validation = self.validate_patient_record(patient_record, outline_key)
            record_logs.append({"attempt": attempt, **validation.model_dump()})
            if validation.passed:
                break
            record_revision_guidance = validation.revision_guidance or validation.issues
        else:
            raise RuntimeError(
                f"Patient record validation failed after {max_retries} attempts."
            )

        for attempt in range(1, max_retries + 1):
            final_record = self.generate_examination_results(
                outline_key,
                patient_record=patient_record,
                seed=seed,
                revision_guidance=exam_revision_guidance,
            )
            validation = self.validate_examination_results(final_record, outline_key)
            exam_logs.append({"attempt": attempt, **validation.model_dump()})
            if validation.passed:
                break
            exam_revision_guidance = validation.revision_guidance or validation.issues
        else:
            raise RuntimeError(
                f"Examination result validation failed after {max_retries} attempts."
            )

        final_record["validation_logs"] = {
            "patient_record": record_logs,
            "examination_results": exam_logs,
        }
        case_index = self._next_case_index(outline_key)
        final_record["metadata"].update(
            {
                "disease_key": outline_key,
                "case_index": case_index,
                "case_id": f"{outline_key}_{case_index}",
            }
        )
        save_json(
            data=final_record,
            output_dir=str(self.final_output_path),
            overwrite=False,
        )
        return final_record

    def generate_character(self):
        if not self.disease_key:
            raise ValueError("PatientZeroGeneratorConfig.disease_key is required.")
        outline_key = self._resolve_outline_key(self.disease_key)
        disease_outlines = (
            load_json(str(self.disease_outline_path))
            if self.disease_outline_path.exists()
            else {}
        )
        if outline_key not in disease_outlines:
            self.generate_disease_outline(self.disease_key)
        return self.generate_static_record(self.disease_key, seed=self.configs.random_seed)
