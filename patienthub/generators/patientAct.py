# coding=utf-8
# Licensed under the MIT License;

import re
import json
import logging
import random
from pathlib import Path
from omegaconf import DictConfig
from dataclasses import dataclass

from patienthub.configs import APIModelConfig
from patienthub.generators.base import BaseGenerator
from patienthub.utils import load_json, dict_to_str
from patienthub.schemas.patientAct import (
    SampledDemographic,
    ProblemFormulation,
    Demographics,
    DemographicCompletionResult,
    PsychologicalFormulation,
    PatientProfile,
    ValidationResult,
    ProfileMemory,
    PatientActCharacter,
    DiseaseOutline,
    CORE_BELIEF_THEMES,
    ATTACHMENT_STYLES,
)

logger = logging.getLogger(__name__)


@dataclass
class PatientActGeneratorConfig(APIModelConfig):
    """Configuration for the PatientAct character generator."""

    agent_name: str = "patientAct"
    prompt_path: str = "data/prompts/generator/patientAct.yaml"
    resource_dir: str = "data/resources/PatientAct"
    # One generator is built per input record, so a fixed seed makes every
    # record in a batch sample the same scaffold. Set it only for single-record
    # reproduction runs.
    random_seed: int | None = None


class PatientActGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        source_dir = Path(self.configs.resource_dir)
        self.rng = random.Random(self.configs.random_seed)

        self.situation: str | None = None
        self.disease_key: str | None = None

        self.attribute_priors = load_json(str(source_dir / "attribute_priors.json"))
        self.disease_attribute_priors = load_json(
            str(source_dir / "disease_priors.json")
        )
        self.disease_outlines = load_json(str(source_dir / "disease_outlines.json"))

    # ── Utilities ─────────────────────────────────────────────────────────

    @staticmethod
    def weighted_choice(distribution: dict[str, float], rng: random.Random) -> str:
        weights = [float(weight) for weight in distribution.values()]
        if sum(weights) <= 0:
            raise ValueError("Weighted distribution must have a positive total.")
        return rng.choices(list(distribution), weights=weights, k=1)[0]

    def generation_outline(self, scaffold: SampledDemographic) -> tuple[str, str]:
        """Slim outline for generation: what the disorder looks like."""
        if not self.disease_key or self.disease_key not in self.disease_outlines:
            return (
                "Not specified",
                "Infer the clinical context from the situation and demographic scaffold.",
            )
        raw = self.disease_outlines[self.disease_key]
        context = {
            "key_characteristics": raw["key_characteristics"],
            "typical_presentation": raw["typical_presentation"],
        }
        if scaffold.age_group in ("Child", "Elderly"):
            context["special_populations"] = raw.get("special_populations", [])
        return self.disease_key, json.dumps(context, indent=2)

    def validation_outline(self) -> tuple[str, str]:
        """Full outline for validation: includes contraindications, differentials, red flags."""
        if not self.disease_key or self.disease_key not in self.disease_outlines:
            return (
                "Not specified",
                "Infer the clinical context from the situation and demographic scaffold.",
            )
        outline = DiseaseOutline.model_validate(self.disease_outlines[self.disease_key])
        return self.disease_key, outline.model_dump_json(indent=2)

    def _core_belief_desc(self, scaffold: SampledDemographic) -> str:
        return CORE_BELIEF_THEMES.get(
            scaffold.core_belief_theme, "Unknown core belief theme."
        )

    def _attachment_desc(self, scaffold: SampledDemographic) -> str:
        return f"{scaffold.attachment_style}, meaning {ATTACHMENT_STYLES.get(scaffold.attachment_style, 'Unknown attachment style.')}"

    @staticmethod
    def hard_conflict_issues(scaffold: SampledDemographic, context: str) -> list[str]:
        text = context.lower()
        alcohol_pattern = r"\b(alcohol|drink|drinking|drunk|wine|beer|vodka|whiskey)\b"
        adult_role_pattern = (
            r"\b(office worker|colleague|coworker|workplace|work stress"
            r"|married|divorced|widowed|husband|wife)\b"
        )
        child_role_pattern = r"\b(kindergarten|middle school|high school child|minor)\b"
        issues = []

        if scaffold.age_group == "Child":
            if scaffold.occupation_type in {
                "Office worker",
                "Service worker",
                "Manual worker",
                "Retired",
            }:
                issues.append(
                    "The sampled occupation is incompatible with a child age group."
                )
            if re.search(alcohol_pattern, text) or re.search(adult_role_pattern, text):
                issues.append(
                    "The sampled child age group conflicts with adult alcohol "
                    "or adult-life evidence in the clinical situation."
                )

        if scaffold.age_group == "Elderly":
            if scaffold.occupation_type == "Student":
                issues.append(
                    "The sampled elderly age group conflicts with "
                    "the student occupation."
                )
            if re.search(child_role_pattern, text):
                issues.append(
                    "The sampled elderly age group conflicts with "
                    "child or adolescent evidence in the clinical situation."
                )

        if scaffold.gender == "male" and re.search(
            r"\b(pregnant|pregnancy|postpartum|menopause)\b", text
        ):
            issues.append(
                "The sampled male gender conflicts with explicit "
                "pregnancy, postpartum, or menopause evidence."
            )

        return issues

    def with_revision_guidance(
        self, prompt: str, revision_guidance: list[str] | None = None
    ) -> str:
        if not revision_guidance:
            return prompt
        guidance = json.dumps(revision_guidance, ensure_ascii=False, indent=2)
        revision_prompt = self.prompts["revision_guidance"].render(
            revision_guidance=guidance
        )
        return f"{prompt}\n\n{revision_prompt}"

    # ── Distribution & Sampling ───────────────────────────────────────────

    def attribute_distributions(
        self,
    ) -> tuple[dict[str, dict[str, float]], dict[str, list[int]]]:
        global_priors = self.attribute_priors["global"]
        overrides = self.disease_attribute_priors.get(self.disease_key, {})
        distributions = {
            "age_group": global_priors["age_group"].copy(),
            "biological_sex": global_priors["biological_sex"].copy(),
            "ethnicity": global_priors["ethnicity"].copy(),
            "occupation_type": global_priors["occupation_type"].copy(),
            "core_belief_theme": global_priors["core_belief_theme"].copy(),
            "attachment_style": global_priors["attachment_style"].copy(),
        }
        for key in distributions:
            if key in overrides:
                distributions[key] = overrides[key]["labels"].copy()
        return distributions, self.attribute_priors["age_ranges"]

    def sample_demographic(self) -> SampledDemographic:
        distributions, age_ranges = self.attribute_distributions()
        age_group = self.weighted_choice(distributions["age_group"], self.rng)
        return SampledDemographic(
            age_group=age_group,
            gender=self.weighted_choice(
                distributions["biological_sex"], self.rng
            ).lower(),
            ethnicity=self.weighted_choice(distributions["ethnicity"], self.rng),
            occupation_type=self.weighted_choice(
                distributions["occupation_type"], self.rng
            ),
            core_belief_theme=self.weighted_choice(
                distributions["core_belief_theme"], self.rng
            ),
            attachment_style=self.weighted_choice(
                distributions["attachment_style"], self.rng
            ),
        )

    # ── Generation Steps ──────────────────────────────────────────────────

    def generate_problem_formulation(
        self,
        scaffold: SampledDemographic,
        revision_guidance: list[str] | None = None,
    ) -> ProblemFormulation:
        disease_key, disease_outline = self.generation_outline(scaffold)
        demo_scaffold = {
            k: v
            for k, v in scaffold.model_dump().items()
            if k not in ["core_belief_theme", "attachment_style"]
        }
        prompt = self.prompts["problem_formulation_generation"].render(
            disease_key=disease_key,
            disease_outline=disease_outline,
            situation=self.situation,
            demographic_scaffold=dict_to_str(demo_scaffold, prefix="    - "),
        )
        prompt = self.with_revision_guidance(prompt, revision_guidance)
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ProblemFormulation,
        )

    def generate_demographics(
        self,
        problem_formulation: ProblemFormulation,
        scaffold: SampledDemographic,
        revision_guidance: list[str] | None = None,
        max_retries: int = 5,
    ) -> Demographics:
        disease_key, disease_outline = self.generation_outline(scaffold)
        problem_formulation_json = problem_formulation.model_dump_json(indent=2)
        conflict_context = f"{self.situation}\n{problem_formulation_json}"
        current_demographics = None
        current_guidance = list(revision_guidance or [])
        current_guidance.extend(self.hard_conflict_issues(scaffold, conflict_context))

        for _ in range(max_retries):
            prompt = self.prompts["demographics_completion"].render(
                disease_key=disease_key,
                disease_outline=disease_outline,
                demographic_scaffold=scaffold.model_dump_json(indent=2),
                current_demographics=(
                    current_demographics.model_dump_json(indent=2)
                    if current_demographics is not None
                    else "null"
                ),
                problem_formulation=problem_formulation_json,
            )
            prompt = self.with_revision_guidance(prompt, current_guidance)
            result = self.chat_model.generate(
                [{"role": "system", "content": prompt}],
                response_format=DemographicCompletionResult,
            )
            if result.passed:
                return result.demographics
            current_demographics = result.demographics or current_demographics
            current_guidance = result.issues
            logger.info("Revising demographics due to conflicts: %s", result.issues)

        logger.warning(
            "Demographics accepted after %d retries with remaining issues: %s",
            max_retries,
            current_guidance,
        )
        return current_demographics

    def generate_psychological_formulation(
        self,
        problem_formulation: ProblemFormulation,
        demographics: Demographics,
        scaffold: SampledDemographic,
        revision_guidance: list[str] | None = None,
    ) -> PsychologicalFormulation:
        disease_key, disease_outline = self.generation_outline(scaffold)
        prompt = self.prompts["psychological_formulation_generation"].render(
            disease_key=disease_key,
            disease_outline=disease_outline,
            demographics=demographics.model_dump_json(indent=2),
            problem_formulation=problem_formulation.model_dump_json(indent=2),
            core_belief_theme=self._core_belief_desc(scaffold),
            attachment_style=self._attachment_desc(scaffold),
        )
        prompt = self.with_revision_guidance(prompt, revision_guidance)
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=PsychologicalFormulation,
        )

    # ── Validation ────────────────────────────────────────────────────────

    def validate_profile(self, profile: PatientProfile) -> ValidationResult:
        disease_key, disease_outline = self.validation_outline()
        prompt = self.prompts["profile_validation"].render(
            disease_key=disease_key,
            disease_outline=disease_outline,
            situation=self.situation,
            profile=profile.model_dump_json(indent=2),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ValidationResult,
        )

    # ── Memory ────────────────────────────────────────────────────────────

    @staticmethod
    def extract_memory_items(profile: PatientProfile) -> list[dict]:
        pf = profile.problem_formulation
        psych = profile.psychological_formulation
        items = []

        for i, item in enumerate(pf.predisposing_factors.psychological):
            items.append(
                {
                    "path": f"problem_formulation.predisposing_factors.psychological.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(pf.predisposing_factors.social):
            items.append(
                {
                    "path": f"problem_formulation.predisposing_factors.social.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(psych.intermediate_beliefs):
            items.append(
                {
                    "path": f"psychological_formulation.intermediate_beliefs.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(psych.automatic_thoughts):
            items.append(
                {
                    "path": f"psychological_formulation.automatic_thoughts.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(psych.triggers):
            items.append(
                {
                    "path": f"psychological_formulation.triggers.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(pf.presenting_problem.impact):
            items.append(
                {
                    "path": f"problem_formulation.presenting_problem.impact.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(pf.perpetuating_factors.internal):
            items.append(
                {
                    "path": f"problem_formulation.perpetuating_factors.internal.{i}",
                    "content": item,
                }
            )
        for i, item in enumerate(pf.perpetuating_factors.external):
            items.append(
                {
                    "path": f"problem_formulation.perpetuating_factors.external.{i}",
                    "content": item,
                }
            )
        for i, pattern in enumerate(psych.interpersonal_patterns):
            if pattern.domain.lower() != "the therapist":
                items.append(
                    {
                        "path": f"psychological_formulation.interpersonal_patterns.{i}",
                        "content": (
                            f"With {pattern.domain}: "
                            f"Wish: {pattern.wish} | "
                            f"Expected response: {pattern.response_of_other} | "
                            f"Reaction: {pattern.response_of_self}"
                        ),
                    }
                )

        return items

    def build_memory(self, profile: PatientProfile) -> ProfileMemory:
        items = self.extract_memory_items(profile)
        prompt = self.prompts["profile_memory"].render(
            profile=profile.model_dump_json(indent=2),
            items=items,
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ProfileMemory,
        )

    # ── Orchestration ─────────────────────────────────────────────────────

    def generate_profile(
        self,
        scaffold: SampledDemographic,
        revision_guidance: list[str] | None = None,
    ) -> PatientProfile:
        problem_formulation = self.generate_problem_formulation(
            scaffold, revision_guidance
        )
        demographics = self.generate_demographics(
            problem_formulation, scaffold, revision_guidance
        )
        psychological_formulation = self.generate_psychological_formulation(
            problem_formulation, demographics, scaffold, revision_guidance
        )
        return PatientProfile(
            demographics=demographics,
            problem_formulation=problem_formulation,
            psychological_formulation=psychological_formulation,
        )

    def generate_with_validation(
        self, max_retries: int = 3
    ) -> tuple[PatientProfile, SampledDemographic]:
        scaffold = self.sample_demographic()
        revision_guidance = None
        profile = None
        for _ in range(max_retries):
            profile = self.generate_profile(
                scaffold, revision_guidance=revision_guidance
            )
            validation = self.validate_profile(profile)
            if validation.passed:
                return profile, scaffold
            revision_guidance = validation.revision_guidance or validation.issues
            logger.info("Profile validation failed: %s", validation.issues)
        logger.warning(
            "Profile accepted after %d retries with remaining issues: %s",
            max_retries,
            revision_guidance,
        )
        return profile, scaffold

    def generate_character(self, data: dict | None = None) -> PatientActCharacter:
        data = data or {}
        self.situation = data.get("situation")
        self.disease_key = data.get("disease_key")
        profile, scaffold = self.generate_with_validation()
        memory = self.build_memory(profile)
        return PatientActCharacter(
            profile=profile,
            memory=memory,
            seed=scaffold,
            situation=self.situation,
            disease_key=self.disease_key,
        )
