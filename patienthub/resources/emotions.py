"""Emotion taxonomies"""

from functools import cached_property
from typing import Literal


class EmotionTaxonomy:
    """Base contract for an emotion taxonomy: a named set of labels exposed as a
    ``typing.Literal`` for structured LLM output."""

    name: str = "emotion-taxonomy"
    labels: list[str] = []

    @cached_property
    def literal(self):
        """A ``typing.Literal`` of every label, for structured LLM output."""
        return Literal[tuple(self.labels)]

    def __contains__(self, label: str) -> bool:
        return label in self.labels


class GoEmotions(EmotionTaxonomy):
    """The 28-label GoEmotions taxonomy: labels grouped into affect categories."""

    name = "GoEmotions"
    categories = {
        "Positive": [
            "admiration",
            "amusement",
            "approval",
            "caring",
            "curiosity",
            "desire",
            "excitement",
            "gratitude",
            "joy",
            "love",
            "optimism",
            "pride",
            "realization",
            "relief",
            "surprise",
        ],
        "Neutral": ["neutral"],
        "Ambiguous": ["confusion", "disappointment", "nervousness"],
        "Negative": [
            "anger",
            "annoyance",
            "disapproval",
            "disgust",
            "embarrassment",
            "fear",
            "sadness",
            "remorse",
            "grief",
        ],
    }

    @cached_property
    def labels(self) -> list[str]:
        """Flat label list, derived from the category grouping."""
        return [emotion for members in self.categories.values() for emotion in members]

    def get_category(self, emotion: str, default: str = "Neutral") -> str:
        """Return the affect category containing ``emotion`` (``default`` if unknown)."""
        for category, members in self.categories.items():
            if emotion in members:
                return category
        return default


GOEMOTIONS = GoEmotions()
