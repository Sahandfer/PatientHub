from omegaconf import DictConfig
from dataclasses import dataclass
from typing import Any

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.schemas.mindVoyager import (
    MindVoyagerDifficultyPreset,
    OpennessAssessment,
    QuestionFacilitationAssessment,
)


@dataclass
class MindVoyagerClientConfig(APIModelConfig):
    """Configuration for the MindVoyagerClient agent."""

    agent_name: str = "mindVoyager"
    prompt_path: str = "data/prompts/client/mindVoyager.yaml"
    data_path: str = "data/characters/mindVoyager.json"
    data_idx: int = 0
    difficulty: str = "custom" # easy/hard/custom


class MindVoyagerClient(BaseClient):
    MAX_EXTERNAL_SITUATIONS = 3
    RAPPORT_CHECK_INTERVAL = 4
    RAPPORT_THRESHOLD = 4
    QUESTION_THRESHOLD = 4
    DIFFICULTY_PRESETS = {
        "easy": {
            "openness": "high",
            "metacognition": "high",
            "initial_visible_external_count": 3,
            "low_metacognition_question_check_interval": 2,
            "high_metacognition_question_check_interval": 1,
        },
        "hard": {
            "openness": "low",
            "metacognition": "low",
            "initial_visible_external_count": 1,
            "low_metacognition_question_check_interval": 2,
            "high_metacognition_question_check_interval": 1,
        },
        "custom": {
            "openness": "low",
            "metacognition": "high",
            "initial_visible_external_count": 2,
            "low_metacognition_question_check_interval": 2,
            "high_metacognition_question_check_interval": 1,
        },
    }
    INTERNAL_REVEAL_ORDER = [
        "relevant_history",
        "core_beliefs",
        "intermediate_beliefs",
        "coping_strategies",
    ]

    def __init__(self, configs: DictConfig):
        self.behavior_settings = self.resolve_difficulty_preset(configs)
        self.visible_external_count = max(
            0, int(self.behavior_settings["initial_visible_external_count"])
        )
        self.visible_internal_keys: set[str] = set()
        self.turn_count = 0
        super().__init__(configs)

    @classmethod
    def resolve_difficulty_preset(cls, configs: DictConfig) -> dict[str, Any]:
        difficulty = str(getattr(configs, "difficulty", "custom")).lower()
        if difficulty not in cls.DIFFICULTY_PRESETS:
            raise ValueError(
                "difficulty must be one of easy, hard, or custom"
            )
        return MindVoyagerDifficultyPreset.model_validate(
            cls.DIFFICULTY_PRESETS[difficulty]
        ).model_dump()

    def visible_internal_value(self, key: str) -> str:
        if key not in self.visible_internal_keys:
            return "unknown"
        value = self.data.get("internal_cognitive_diagram", {}).get(key, "")
        if isinstance(value, list):
            return "; ".join(str(item) for item in value if item)
        return str(value) if value else "unknown"

    def visible_experience(self, index: int) -> dict[str, str]:
        experiences = self.data.get("external_experiences", [])
        if index < self.visible_external_count and index < len(experiences):
            experience = experiences[index]
            return {
                "situation": str(experience.get("situation", "unknown")),
                "reaction": str(experience.get("reaction", "unknown")),
            }
        return {"situation": "unknown", "reaction": "unknown"}

    def build_sys_prompt(self):
        first = self.visible_experience(0)
        second = self.visible_experience(1)
        third = self.visible_experience(2)
        prompt = self.prompts["system_prompt"].render(
            name=self.data.get("name", "Client"),
            openness=str(self.behavior_settings.get("openness", "low")),
            metacognition=str(self.behavior_settings.get("metacognition", "low")),
            history=self.visible_internal_value("relevant_history"),
            belief="; ".join(
                item
                for item in [
                    self.visible_internal_value("core_beliefs"),
                    self.visible_internal_value("intermediate_beliefs"),
                ]
                if item
            ),
            strategy=self.visible_internal_value("coping_strategies"),
            situation1=first["situation"],
            reaction1=first["reaction"],
            situation2=second["situation"],
            reaction2=second["reaction"],
            situation3=third["situation"],
            reaction3=third["reaction"],
        )
        system_message = {"role": "system", "content": prompt}
        if not getattr(self, "messages", None):
            self.messages = [system_message]
        elif self.messages[0].get("role") == "system":
            self.messages[0] = system_message
        else:
            self.messages.insert(0, system_message)

    def reveal_next_external(self) -> bool:
        max_visible = min(
            self.MAX_EXTERNAL_SITUATIONS,
            len(self.data.get("external_experiences", [])),
        )
        if self.visible_external_count >= max_visible:
            return False
        self.visible_external_count += 1
        return True

    def reveal_internal(self) -> bool:
        for key in self.INTERNAL_REVEAL_ORDER:
            if key not in self.visible_internal_keys:
                self.visible_internal_keys.add(key)
                return True
        return False

    def run_mediator_checks(self) -> None:
        dialogue = "\n".join(
            "{}: {}".format(
                "Client" if item["role"] == "assistant" else "Therapist",
                item["content"],
            )
            for item in self.messages[1:]
            if item["role"] in {"user", "assistant"}
        )
        if not dialogue:
            return

        rapport_interval = self.RAPPORT_CHECK_INTERVAL
        if rapport_interval > 0 and self.turn_count % rapport_interval == 0:
            prompt = self.prompts["openness_critic_prompt"].render(
                dialogue_context=dialogue
            )
            result = self.chat_model.generate(
                [{"role": "user", "content": prompt}],
                response_format=OpennessAssessment,
            )
            if int(result.rating) >= self.RAPPORT_THRESHOLD:
                self.reveal_next_external()

        if str(self.behavior_settings.get("metacognition", "low")).lower() == "high":
            question_interval = int(
                self.behavior_settings.get(
                    "high_metacognition_question_check_interval", 1
                )
            )
        else:
            question_interval = int(
                self.behavior_settings.get(
                    "low_metacognition_question_check_interval", 2
                )
            )
        if question_interval > 0 and self.turn_count % question_interval == 0:
            prompt = self.prompts["question_facilitation_prompt"].render(
                dialogue_history=dialogue
            )
            result = self.chat_model.generate(
                [{"role": "user", "content": prompt}],
                response_format=QuestionFacilitationAssessment,
            )
            if int(result.rating) >= self.QUESTION_THRESHOLD:
                self.reveal_internal()

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        self.turn_count += 1
        self.run_mediator_checks()
        self.build_sys_prompt()
        res = self.chat_model.generate(self.messages)
        content = res.content if hasattr(res, "content") else str(res)
        self.messages.append({"role": "assistant", "content": content})
        return res

    def reset(self) -> None:
        self.behavior_settings = self.resolve_difficulty_preset(self.configs)
        self.visible_external_count = max(
            0, int(self.behavior_settings["initial_visible_external_count"])
        )
        self.visible_internal_keys = set()
        self.messages = []
        self.turn_count = 0
        super().reset()
