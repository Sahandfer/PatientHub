# coding=utf-8
# Licensed under the MIT License;

"""Patient-Zero Generator - Creates standardized static patient-record scaffolds."""

import json
import random

from pathlib import Path
from omegaconf import DictConfig
from dataclasses import dataclass
from typing import Literal, Any
from pydantic import BaseModel, Field, model_validator

from .base import BaseGenerator
import patienthub.schemas.patientZero as pz
from patienthub.configs import APIModelConfig
from patienthub.resources import PHQ9, GAD7, ISI
from patienthub.utils import load_json, save_json


@dataclass
class PatientZeroGeneratorConfig(APIModelConfig):
    """Configuration for the Patient-Zero generator."""

    agent_name: str = "patientZero"
    prompt_path: str = "data/prompts/generator/patientZero.yaml"
    resource_dir: str = "data/resources/PatientZero"


class ValidationResult(BaseModel):

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


class PatientZeroGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

        source_dir = self.configs.resource_dir
        self.disease_key = self.configs.disease_key

        # Load static resources once at init
        self.raw_outlines = load_json(f"{source_dir}/raw_outlines.json")
        self.attribute_priors = load_json(f"{source_dir}/demo_priors.json")
        self.disease_attribute_priors = load_json(f"{source_dir}/disease_priors.json")
        self.exam_references = load_json(f"{source_dir}/exam_references.json")
        self.disease_outline_path = f"{source_dir}/disease_outlines.json"
        self.disease_outlines: dict = (
            load_json(self.disease_outline_path)
            if Path(self.disease_outline_path).exists()
            else {}
        )
        self.scales = {
            scale.name: {"range": list(scale.score_range), "bands": scale.bands}
            for scale in (PHQ9, GAD7, ISI)
        }

    @staticmethod
    def weighted_choice(distribution: dict[str, float], rng: random.Random) -> str:
        weights = [float(weight) for weight in distribution.values()]
        if sum(weights) <= 0:
            raise ValueError("Weighted distribution must have a positive total.")
        return rng.choices(list(distribution), weights=weights, k=1)[0]

    def attribute_distributions(self) -> tuple[dict, dict]:
        distributions = {
            key: value.copy() for key, value in self.attribute_priors["global"].items()
        }
        overrides = self.disease_attribute_priors.get(self.disease_key, {})
        for key, value in overrides.items():
            if isinstance(value, dict) and "labels" in value:
                value = value["labels"]
            distributions[key] = value.copy()
        return distributions, self.attribute_priors["age_ranges"]

    def exam_reference(self) -> dict:
        disease_ref = self.exam_references["diseases"].get(self.disease_key, {})
        selected_scales = disease_ref.get("selected_scales", [])
        return {
            "scale_pool": {
                scale: self.scales[scale]
                for scale in selected_scales
                if scale in self.scales
            },
            "disease_reference": disease_ref,
        }

    def with_revision_guidance(
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

    def generate_disease_outline(self) -> pz.DiseaseOutline:
        """Generate a standardized Stage I disease outline for a disease."""

        data = self.raw_outlines[self.disease_key]
        raw_outline = data.get("raw_outline", data)
        prompt = self.prompts["disease_outline_generation"].render(
            disease_name=data.get("disease_name", self.disease_key),
            raw_outline=json.dumps(raw_outline, ensure_ascii=False, indent=2),
        )
        outline = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=pz.DiseaseOutline,
        )
        self.disease_outlines[self.disease_key] = outline.model_dump()
        save_json(
            data=self.disease_outlines,
            output_dir=self.disease_outline_path,
            overwrite=True,
        )
        return outline

    def sample_patient_attributes(
        self,
        severity_level: Literal["mild", "moderate", "severe"] | None = None,
        max_retries: int = 100,
    ) -> pz.PatientAttributes:
        """Sample a valid Patient-Zero Stage II attribute vector."""

        disease_name = self.raw_outlines[self.disease_key].get(
            "disease_name", self.disease_key
        )
        distributions, age_ranges = self.attribute_distributions()
        rng = random.Random(self.random_seed)

        for _ in range(max_retries):
            age_strata = self.weighted_choice(distributions["age_strata"], rng)
            age_min, age_max = age_ranges[age_strata]
            data = {
                key: self.weighted_choice(dist, rng)
                for key, dist in distributions.items()
                if key not in ("age_strata", "severity_level")
            }
            data.update(
                {
                    "disease_name": disease_name,
                    "severity_level": severity_level
                    or self.weighted_choice(distributions["severity_level"], rng),
                    "age_strata": age_strata,
                    "age": rng.randint(age_min, age_max),
                }
            )
            try:
                return pz.PatientAttributes(**data)
            except ValueError:
                continue

        raise RuntimeError(
            f"Failed to sample a valid Patient-Zero attribute vector for {self.disease_key}."
        )

    def generate_patient_record_symptoms(
        self,
        attributes: pz.PatientAttributes | dict | None = None,
        revision_guidance: list[str] | None = None,
    ) -> dict:
        """Generate Stage III patient profile and symptom trajectory."""

        if attributes is None:
            attributes = self.sample_patient_attributes()
        elif isinstance(attributes, dict):
            attributes = pz.PatientAttributes(**attributes)

        outline = pz.DiseaseOutline.model_validate(
            self.disease_outlines[self.disease_key]
        )
        prompt = self.prompts["patient_record_symptom_generation"].render(
            disease_name=attributes.disease_name,
            severity_level=attributes.severity_level,
            patient_attributes=attributes.model_dump_json(indent=2),
            symptoms_list=json.dumps(
                self.raw_outlines[self.disease_key]
                .get("raw_outline", {})
                .get("common_symptoms", []),
                ensure_ascii=False,
                indent=2,
            ),
            disease_outline=outline.model_dump_json(indent=2),
        )
        prompt = self.with_revision_guidance(prompt, revision_guidance)
        record = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=pz.PatientRecordAndSymptoms,
        )

        demographics = attributes.model_dump(exclude={"disease_name", "severity_level"})
        profile = {**demographics, **record.patient_profile.model_dump()}
        trajectory = {
            **record.symptom_trajectory.model_dump(),
            "current_severity": attributes.severity_level,
        }
        return {
            "metadata": {
                "disease_name": attributes.disease_name,
                "disease_key": self.disease_key,
                "severity_level": attributes.severity_level,
                "disease_outline_id": f"{self.disease_key}.json",
                "seed": self.random_seed,
            },
            "sampled_attributes": attributes.model_dump(),
            "patient_profile": profile,
            "symptom_trajectory": trajectory,
        }

    def generate_examination_results(
        self,
        patient_record: dict,
        revision_guidance: list[str] | None = None,
    ) -> dict:
        """Generate Stage IV examination results in one LLM call."""

        outline = pz.DiseaseOutline.model_validate(
            self.disease_outlines[self.disease_key]
        )
        prompt = self.prompts["examination_result_generation"].render(
            disease_name=patient_record["metadata"]["disease_name"],
            severity_level=patient_record["metadata"]["severity_level"],
            patient_record=json.dumps(patient_record, ensure_ascii=False, indent=2),
            disease_outline=outline.model_dump_json(indent=2),
            exam_reference=json.dumps(
                self.exam_reference(),
                ensure_ascii=False,
                indent=2,
            ),
        )
        prompt = self.with_revision_guidance(prompt, revision_guidance)
        results = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=pz.ExaminationResults,
        )

        return {
            **patient_record,
            "examination_results": results.model_dump(),
        }

    def validate_patient_record(
        self,
        patient_record: dict,
        revision_guidance: list[str] | None = None,
    ) -> ValidationResult:
        """Validate Stage III profile and symptom content."""

        outline = pz.DiseaseOutline.model_validate(
            self.disease_outlines[self.disease_key]
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
            response_format=ValidationResult,
        )

    def validate_examination_results(
        self,
        patient_record: dict,
        revision_guidance: list[str] | None = None,
    ) -> ValidationResult:
        """Validate Stage IV examination results."""

        outline = pz.DiseaseOutline.model_validate(
            self.disease_outlines[self.disease_key]
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
                self.exam_reference(),
                ensure_ascii=False,
                indent=2,
            ),
            disease_outline=outline.model_dump_json(indent=2),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ValidationResult,
        )

    def generate_with_validation(
        self,
        generate_fn,
        validate_fn,
        error_msg: str,
        max_retries: int = 3,
    ) -> tuple[dict, list[dict]]:
        """Run a generate→validate retry loop, returning the result and logs."""
        logs = []
        revision_guidance = None
        for attempt in range(1, max_retries + 1):
            result = generate_fn(revision_guidance=revision_guidance)
            validation = validate_fn(result)
            logs.append({"attempt": attempt, **validation.model_dump()})
            if validation.passed:
                return result, logs
            revision_guidance = validation.revision_guidance or validation.issues
        raise RuntimeError(error_msg)

    def generate_static_record(self, max_retries: int = 3) -> dict:
        """Generate final static Patient-Zero record P={B,S,E} with validation."""

        attributes = self.sample_patient_attributes()

        patient_record, record_logs = self.generate_with_validation(
            generate_fn=lambda **kw: self.generate_patient_record_symptoms(
                attributes=attributes, **kw
            ),
            validate_fn=self.validate_patient_record,
            error_msg=f"Patient record validation failed after {max_retries} attempts.",
            max_retries=max_retries,
        )
        final_record, exam_logs = self.generate_with_validation(
            generate_fn=lambda **kw: self.generate_examination_results(
                patient_record=patient_record, **kw
            ),
            validate_fn=self.validate_examination_results,
            error_msg=f"Examination result validation failed after {max_retries} attempts.",
            max_retries=max_retries,
        )

        final_record["validation_logs"] = {
            "patient_record": record_logs,
            "examination_results": exam_logs,
        }
        final_record["metadata"].update(
            {
                "disease_key": self.disease_key,
                "case_id": self.disease_key,
            }
        )
        return pz.PatientZeroCharacter.model_validate(final_record).model_dump()

    def generate_character(self, data: dict[str, Any]) -> pz.PatientZeroCharacter:
        self.disease_key = data.get("disease_key", "")
        self.random_seed = data.get("random_seed", None)
        if not self.disease_key:
            raise ValueError("disease_key is required.")
        if self.disease_key not in self.disease_outlines:
            self.generate_disease_outline()
        return self.generate_static_record()
