from dataclasses import dataclass
from typing import Any

from omegaconf import DictConfig

from .base import BaseClient
from patienthub.configs import APIModelConfig


@dataclass
class DeprofileClientConfig(APIModelConfig):
    """Configuration for the Deprofile patient simulation client."""

    agent_name: str = "deprofile"
    prompt_path: str = "data/prompts/client/deprofile.yaml"
    data_path: str = "data/characters/Deprofile.json"
    data_idx: int = 0
    max_dialogue_snippets: int = 10
    max_timeline_items: int = 50


class DeprofileClient(BaseClient):
    """G7-style Deprofile patient simulator."""

    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    @staticmethod
    def _trait_level(value: float) -> str:
        if value <= 2:
            return "Low"
        if value <= 5:
            return "Medium"
        return "High"

    @classmethod
    def _big_five_traits(cls, big_five: dict[str, Any]) -> list[dict[str, Any]]:
        ordered = [
            "Openness",
            "Conscientiousness",
            "Extraversion",
            "Agreeableness",
            "Neuroticism",
        ]
        traits = []
        for trait in ordered:
            value = big_five.get(trait)
            if value is None:
                continue
            level = cls._trait_level(float(value))
            traits.append({"name": trait, "level": level, "value": value})
        return traits

    @staticmethod
    def _select_messages(
        messages: list[dict[str, Any]], limit: int
    ) -> list[dict[str, str]]:
        return [
            {
                "role": str(item.get("role", "unknown")),
                "content": str(item.get("content", "")).strip(),
            }
            for item in messages[: max(0, limit)]
            if item.get("content")
        ]

    @staticmethod
    def _select_life_event_items(
        timeline_memory: dict[str, Any] | None,
        timeline: dict[str, Any],
        limit: int,
    ) -> list[dict[str, Any]]:
        memory_cards = (
            (timeline_memory or {}).get("life_event", {}).get("cards", [])
        )
        if memory_cards and limit > 0:
            selected_cards = memory_cards[-limit:]
            return [
                {
                    "episode_id": card.get("episode_id"),
                    "time_range": card.get("time_range"),
                    "card_text": card.get("card_text"),
                }
                for card in selected_cards
                if card.get("card_text")
            ]

        items = timeline.get("timeline", [])
        if not items or limit <= 0:
            return []
        selected = items[-limit:]
        return [
            {
                "timestamp": item.get("timestamp"),
                "life_event": item.get("life_event"),
                "tweet": item.get("tweet"),
            }
            for item in selected
        ]

    def _prompt_context(self) -> dict[str, Any]:
        profile = self.data["clinical_profile"]
        return {
            "profile": profile,
            "age": profile["age"],
            "gender": profile["gender"],
            "marital_status": profile["marital_status"],
            "work_status": profile["work_status"],
            "depression_risk": profile["depression_risk"],
            "suicide_risk": profile["suicide_risk"],
            "big_five_traits": self._big_five_traits(profile.get("big_five", {})),
            "positive_symptoms": profile.get("positive_symptoms", []),
            "negative_symptoms": profile.get("negative_symptoms", []),
            "clinical_summary": profile.get("summation") or "",
            "assessment_messages": self._select_messages(
                self.data.get("assessment_dialogue", []),
                int(getattr(self.configs, "max_dialogue_snippets", 10)),
            ),
            "counseling_messages": self._select_messages(
                self.data.get("counseling_dialogue", []),
                int(getattr(self.configs, "max_dialogue_snippets", 10)),
            ),
            "life_event_items": self._select_life_event_items(
                self.data.get("timeline_memory"),
                self.data.get("life_event_timeline", {}),
                int(getattr(self.configs, "max_timeline_items", 50)),
            ),
            "lang": self.configs.lang,
        }

    def build_sys_prompt(self):
        prompt = self.prompts["system_prompt"].render(**self._prompt_context())
        self.messages = [{"role": "system", "content": prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        return res
