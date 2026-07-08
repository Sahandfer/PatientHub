# coding=utf-8
# Licensed under the MIT License;

"""MindVoyager Client - progressively disclosed cognitive-diagram patient simulation.

Paper: "Can You Share Your Story? Modeling Clients' Metacognition and Openness
       for LLM Therapist Evaluation" (ACL 2025 Findings)
       https://aclanthology.org/2025.findings-acl.1332/

MindVoyager simulates a therapy client whose cognitive conceptualization diagram
is masked at the start of the session and progressively disclosed as the dialogue
earns it, rather than exposed upfront. A cognition mediator periodically judges
the conversation and unmasks parts of the diagram.

Key Features:
- Masked cognitive diagram: internal elements start hidden (rendered as "unknown")
- Rapport-gated external disclosure: one more situation unlocks as openness grows
- Metacognition-gated internal disclosure: the full internal diagram unlocks when
  the therapist's questions facilitate deep exploration
- Difficulty presets: easy, normal, hard, custom (controlling openness,
  metacognition, and initial visibility)
"""

from omegaconf import DictConfig
from dataclasses import dataclass
import logging
from typing import Any

from .base import BaseClient
from patienthub.utils import flatten_conv
import patienthub.schemas.mindVoyager as mv
from patienthub.configs import APIModelConfig

logger = logging.getLogger(__name__)


@dataclass
class MindVoyagerClientConfig(APIModelConfig):
    """Configuration for the MindVoyagerClient agent."""

    agent_name: str = "mindVoyager"
    prompt_path: str = "data/prompts/client/mindVoyager.yaml"
    data_path: str = "data/characters/mindVoyager.json"
    data_idx: int = 0
    preset_level: str = "easy"


class MindVoyagerClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.init_session_state(configs)
        super().__init__(configs)

    def init_session_state(self, configs: DictConfig) -> None:
        self.behavior_settings = self.set_difficulty(configs.preset_level)
        self.visible_external_count = self.behavior_settings["visible_external_count"]
        self.visible_internal_keys: set[str] = set()
        self.messages: list[dict[str, str]] = []
        self.turn_count = 0

    def set_difficulty(self, preset_level: str) -> dict[str, Any]:
        diff_presets = mv.DIFFICULTY_PRESETS
        if preset_level not in diff_presets:
            raise ValueError(
                f"Preset level must be one of {', '.join(diff_presets.keys())}"
            )
        return diff_presets[preset_level]

    def visible_internal_value(self, key: str) -> str:
        if key not in self.visible_internal_keys:
            return "unknown"
        value = self.data.get("internal_cognitive_diagram", {}).get(key, "")
        if isinstance(value, list):
            return "; ".join(str(item) for item in value if item)
        return str(value) if value else "unknown"

    def visible_experiences(self) -> list[dict[str, Any]]:
        all_exps = self.data.get("external_experiences", [])
        visible_exps = []
        for idx, exp in enumerate(all_exps):
            if idx < self.visible_external_count:
                situation = exp["situation"]
                reaction = exp["reaction"]
            else:
                situation = reaction = "unknown"
            visible_exps.append(
                {"number": idx + 1, "situation": situation, "reaction": reaction}
            )
        return visible_exps

    def build_sys_prompt(self):
        prompt = self.prompts["system_prompt"].render(
            name=self.data.get("name"),
            openness=str(self.behavior_settings.get("openness", "low")),
            metacognition=str(self.behavior_settings.get("metacognition", "low")),
            history=self.visible_internal_value("relevant_history"),
            core_belief=self.visible_internal_value("core_beliefs"),
            intermediate_belief=self.visible_internal_value("intermediate_beliefs"),
            strategy=self.visible_internal_value("coping_strategies"),
            external_experiences=self.visible_experiences(),
        )
        system_message = {"role": "system", "content": prompt}
        if self.messages:
            self.messages[0] = system_message
        else:
            self.messages = [system_message]

    def reveal_next_external(self) -> bool:
        max_visible = len(self.data.get("external_experiences", []))
        if self.visible_external_count >= max_visible:
            return False
        self.visible_external_count += 1
        logger.info(
            "Revealed external experience %d/%d",
            self.visible_external_count,
            max_visible,
        )
        return True

    def reveal_internal(self) -> bool:
        reveal_order = mv.INTERNAL_REVEAL_ORDER
        if self.visible_internal_keys.issuperset(reveal_order):
            return False
        self.visible_internal_keys.update(reveal_order)
        logger.info(
            "Revealed full internal cognitive diagram (%d elements)",
            len(reveal_order),
        )
        return True

    def run_mediator_checks(self) -> None:
        roles = {"assistant": "Client", "user": "Therapist"}
        conv = flatten_conv(self.messages, roles=roles)
        revealed = False

        if self.turn_count % mv.CONSTANTS["rapport_interval"] == 0:
            prompt = self.prompts["openness_critic_prompt"].render(conv=conv)
            result = self.chat_model.generate(
                [{"role": "user", "content": prompt}],
                response_format=mv.OpennessAssessment,
            )
            if result.rating >= mv.CONSTANTS["rapport_threshold"]:
                revealed |= self.reveal_next_external()

        if self.behavior_settings["metacognition"] == "high":
            question_interval = self.behavior_settings[
                "high_metacognition_question_check_interval"
            ]
        else:
            question_interval = self.behavior_settings[
                "low_metacognition_question_check_interval"
            ]
        if question_interval > 0 and self.turn_count % question_interval == 0:
            prompt = self.prompts["question_facilitation_prompt"].render(conv=conv)
            result = self.chat_model.generate(
                [{"role": "user", "content": prompt}],
                response_format=mv.QuestionFacilitationAssessment,
            )
            if result.rating >= mv.CONSTANTS["question_threshold"]:
                revealed |= self.reveal_internal()

        # Only re-render the system prompt when the visible diagram changes
        if revealed:
            self.build_sys_prompt()

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        self.turn_count += 1
        self.run_mediator_checks()
        return res

    def reset(self) -> None:
        self.init_session_state(self.configs)
        super().reset()
