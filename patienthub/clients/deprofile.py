from dataclasses import dataclass
from typing import Any

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.schemas.deprofile import (
    SOCIAL_SYMPTOM_TO_CLINICAL,
    days_to_relative,
    get_constant_dict,
)


@dataclass
class DeprofileClientConfig(APIModelConfig):
    """Configuration for the Deprofile patient simulation client."""

    agent_name: str = "deprofile"
    prompt_path: str = "data/prompts/client/deprofile.yaml"
    data_path: str = "data/characters/deprofile.json"
    data_idx: int = 0
    max_dialogue_snippets: int = 10
    max_timeline_items: int = 50


class DeprofileClient(BaseClient):
    """Deprofile patient simulator.

    Follows the upstream G6 path: clinical pos/neg symptoms are rendered as
    natural-language descriptions (with the symptom timeline woven into the
    positive symptoms), and the life-event timeline is injected as rendered
    memory cards (``life_event_rendering_card``).
    """

    def get_big_five_traits(
        self, big_five: dict[str, Any], lang: str = "zh"
    ) -> list[dict[str, Any]]:
        bfi_guidance = get_constant_dict("BFI", lang)
        traits = []
        for trait in bfi_guidance.keys():
            raw_val = big_five.get(trait)
            if raw_val is None:
                continue
            value = float(raw_val)
            trait_level = "Low" if value <= 2 else "Medium" if value <= 5 else "High"
            traits.append(
                {
                    "name": trait,
                    "level": trait_level,
                    "value": value,
                    "guidance": bfi_guidance.get(trait, {}).get(trait_level, ""),
                }
            )
        return traits

    def select_messages(self, message_type: str) -> list[dict[str, str]]:
        messages = self.data.get(message_type, [])
        limit = int(getattr(self.configs, "max_dialogue_snippets", 10))
        return [
            {
                "role": str(item.get("role", "unknown")),
                "content": str(item.get("content", "")).strip(),
            }
            for item in messages[: max(0, limit)]
            if item.get("content")
        ]

    def symptom_timeline_index(
        self,
    ) -> tuple[dict[str, list[str]], dict[str, dict[str, Any]]]:
        """Return (by_symptom index, nodes-by-id) for the symptom timeline graph."""
        timeline_memory = self.data.get("timeline_memory") or {}
        graph = (timeline_memory.get("symptom") or {}).get("graph", {})
        by_symptom = (graph.get("index", {}) or {}).get("by_symptom") or {}
        nodes_by_id = {node["id"]: node for node in graph.get("nodes", [])}
        return by_symptom, nodes_by_id

    def render_clinical_symptoms(
        self, profile: dict[str, Any]
    ) -> tuple[list[str], list[str], list[str]]:
        """Render pos/neg clinical symptoms as natural language.

        Mirrors upstream ``clinical_prompt``: positive symptoms use their
        ``symptom_descriptions`` text (from constants.json), and where a
        symptom maps to a social label present in the symptom timeline, the
        extracted triples and relative times are appended. Timeline symptoms not
        tied to a listed positive symptom are returned as extra timeline lines.
        """
        by_symptom, nodes_by_id = self.symptom_timeline_index()
        descriptions = get_constant_dict("symptom_descriptions", self.configs.lang)
        used_social: set[str] = set()
        clinical_to_social = {
            clinical: social for social, clinical in SOCIAL_SYMPTOM_TO_CLINICAL.items()
        }

        def timeline_lines(social_label: str) -> list[str]:
            lines = []
            for node_id in by_symptom.get(social_label, []):
                node = nodes_by_id.get(node_id, {})
                triple = node.get("triple")
                time_norm = node.get("time_norm", {}) or {}
                relative = days_to_relative(
                    time_norm.get("days_ago"), lang=self.configs.lang
                )
                if triple and relative:
                    lines.append(f"{relative}：{triple}")
            return lines

        positive: list[str] = []
        for symptom in profile.get("positive_symptoms", []):
            base = descriptions.get(symptom, {}).get("positive", symptom)
            social_label = clinical_to_social.get(symptom)
            lines = timeline_lines(social_label) if social_label else []
            if social_label and social_label in by_symptom:
                used_social.add(social_label)
            if lines:
                positive.append(f"{base}（时间线：{'；'.join(lines)}）")
            else:
                positive.append(base)

        negative = [
            descriptions.get(symptom, {}).get("negative", symptom)
            for symptom in profile.get("negative_symptoms", [])
        ]

        extra: list[str] = []
        for social_label in by_symptom:
            if social_label in used_social:
                continue
            lines = timeline_lines(social_label)
            if lines:
                extra.append(f"[{social_label}]：{'；'.join(lines)}")
        return positive, negative, extra

    def select_life_event_items(self) -> list[dict[str, Any]]:
        timeline_memory = self.data.get("timeline_memory")
        life_event_timeline = self.data.get("life_event_timeline", {})
        limit = int(getattr(self.configs, "max_timeline_items", 50))
        memory_cards = ((timeline_memory or {}).get("life_event") or {}).get(
            "cards", []
        )
        if memory_cards and limit > 0:
            selected_cards = memory_cards[:limit]
            return [
                {
                    "episode_id": card.get("episode_id"),
                    "time_range": card.get("time_range"),
                    "card_text": card.get("card_text"),
                }
                for card in selected_cards
                if card.get("card_text")
            ]

        items = life_event_timeline.get("timeline", [])
        if not items or limit <= 0:
            return []

        anchor = max(item.get("timestamp", 0) for item in items)
        recent_first = sorted(
            items, key=lambda item: item.get("timestamp", 0), reverse=True
        )[:limit]
        return [
            {
                "days_ago": max(0, anchor - item.get("timestamp", anchor)),
                "life_event": item.get("life_event"),
                "tweet": item.get("tweet"),
            }
            for item in recent_first
        ]

    def build_sys_prompt(self):
        profile = self.data["clinical_profile"]
        positive_symptoms, negative_symptoms, extra_symptom_timeline = (
            self.render_clinical_symptoms(profile)
        )
        data = {
            "profile": profile,
            "age": profile["age"],
            "gender": profile["gender"],
            "marital_status": profile["marital_status"],
            "work_status": profile["work_status"],
            "depression_risk": profile["depression_risk"],
            "suicide_risk": profile["suicide_risk"],
            "big_five_traits": self.get_big_five_traits(
                profile.get("big_five", {}), self.configs.lang
            ),
            "positive_symptoms": positive_symptoms,
            "negative_symptoms": negative_symptoms,
            "extra_symptom_timeline": extra_symptom_timeline,
            "clinical_summary": profile.get("summation") or "",
            "assessment_messages": self.select_messages("assessment_dialogue"),
            "counseling_messages": self.select_messages("counseling_dialogue"),
            "life_event_items": self.select_life_event_items(),
            "lang": self.configs.lang,
        }
        prompt = self.prompts["system_prompt"].render(**data)
        self.messages = [{"role": "system", "content": prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        return res
