from dataclasses import dataclass
import json
from typing import Any

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.schemas.cars import (
    CarsCharacter,
    CognitivePatternGenerationOutput,
    PersonaGenerationOutput,
)


@dataclass
class CarsGeneratorConfig(APIModelConfig):
    """Configuration for the CARS profile generator scaffold."""

    agent_name: str = "cars"
    prompt_path: str = "data/prompts/generator/cars.yaml"


class CarsGenerator(BaseGenerator):
    """Generates CARS character profiles in two paper-described stages:
    persona generation from a main CCD and seed sentences, followed by
    session-specific cognitive pattern generation from the persona, CCD, and
    a dialogue excerpt.
    """

    def generate_persona(
        self, main_ccd: Any, sentences: Any
    ) -> PersonaGenerationOutput:
        prompt = self.prompts["persona_generation_prompt"].render(
            main_ccd=self._as_prompt_text(main_ccd),
            sentences=self._as_prompt_text(sentences),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=PersonaGenerationOutput,
        )

    def generate_cognitive_patterns(
        self,
        persona: PersonaGenerationOutput,
        main_ccd: Any,
        dialogue_excerpt: Any,
    ) -> CognitivePatternGenerationOutput:
        prompt = self.prompts["cognitive_pattern_generation_prompt"].render(
            persona=self._as_prompt_text(persona),
            main_ccd=self._as_prompt_text(main_ccd),
            story=self._as_prompt_text(dialogue_excerpt),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=CognitivePatternGenerationOutput,
        )

    def generate_character(self, data: dict[str, Any]) -> CarsCharacter:
        main_ccd = data["main_ccd"]
        sentences = data["mesc_sentences"]
        dialogue_excerpt = data["dialogue_excerpt"]
        persona = self.generate_persona(main_ccd, sentences)
        cognitive_patterns = self.generate_cognitive_patterns(
            persona, main_ccd, dialogue_excerpt
        )

        return CarsCharacter(
            name=persona.name,
            persona=persona,
            background=cognitive_patterns.background,
            main_ccd=main_ccd,
            session_ccd=cognitive_patterns.session_ccd,
            preferences=cognitive_patterns.preferences,
            client_characteristics=cognitive_patterns.client_characteristics,
        )

    def _as_prompt_text(self, value: Any) -> str:
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        return json.dumps(value, ensure_ascii=False, indent=2)
