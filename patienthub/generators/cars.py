from dataclasses import dataclass
import json
from typing import Any

from omegaconf import DictConfig

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.schemas.cars import (
    CarsCharacter,
    CarsCognitivePatternGenerationOutput,
    CarsPersonaGenerationOutput,
)


@dataclass
class CarsGeneratorConfig(APIModelConfig):
    """Configuration for the CARS profile generator scaffold."""

    agent_name: str = "cars"
    prompt_path: str = "data/prompts/generator/cars.yaml"


class CarsGenerator(BaseGenerator):
    """Scaffold for generating CARS character profiles.

    CARS profile generation requires two paper-described stages:
    persona generation from a main CCD and seed sentences, followed by
    session-specific cognitive pattern generation from the persona, CCD, and
    a dialogue excerpt. The scaffold is registered so the implementation can
    be filled in without changing PatientHub's CLI/registry surface later.
    """

    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def generate_persona(
        self, main_ccd: Any, sentences: Any
    ) -> CarsPersonaGenerationOutput:
        prompt = self.prompts["persona_generation_prompt"].render(
            main_ccd=self._as_prompt_text(main_ccd),
            sentences=self._as_prompt_text(sentences),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=CarsPersonaGenerationOutput,
        )

    def generate_cognitive_patterns(
        self,
        persona: CarsPersonaGenerationOutput,
        main_ccd: Any,
        dialogue_excerpt: Any,
    ) -> CarsCognitivePatternGenerationOutput:
        prompt = self.prompts["cognitive_pattern_generation_prompt"].render(
            persona=self._as_prompt_text(persona),
            main_ccd=self._as_prompt_text(main_ccd),
            story=self._as_prompt_text(dialogue_excerpt),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=CarsCognitivePatternGenerationOutput,
        )

    def generate_character(self, data: dict[str, Any]) -> CarsCharacter:
        main_ccd = data["main_ccd"]
        sentences = data["mesc_sentences"]
        dialogue_excerpt = data["dialogue_excerpt"]

        persona = self.generate_persona(main_ccd, sentences)
        cognitive_patterns = self.generate_cognitive_patterns(
            persona, main_ccd, dialogue_excerpt
        )
        return self.assemble_character(persona, cognitive_patterns, main_ccd)

    def assemble_character(
        self,
        persona: CarsPersonaGenerationOutput,
        cognitive_patterns: CarsCognitivePatternGenerationOutput,
        main_ccd: Any,
    ) -> CarsCharacter:
        return CarsCharacter(
            name=persona.name,
            demographics={
                "age": persona.age,
                "gender": persona.gender,
                "occupation": persona.occupation,
            },
            persona=persona,
            background=cognitive_patterns.background,
            main_cognitive_conceptualization_diagram=main_ccd,
            session_specific_cognitive_conceptualization_diagram=(
                cognitive_patterns.session_specific_cognitive_conceptualization_diagram
            ),
            preferences=cognitive_patterns.preferences,
            client_characteristics=cognitive_patterns.client_characteristics,
        )

    def _as_prompt_text(self, value: Any) -> str:
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        return json.dumps(value, ensure_ascii=False, indent=2)
