# coding=utf-8
# Licensed under the MIT License;

"""CARS Client - CBT-grounded resistance-aware patient simulation.

Paper: "When Clients Stop Following: A Cognitive Conceptualization Diagram-driven
       Framework for Strategic Counseling" (2026)
       https://arxiv.org/abs/2606.04389

CARS (Cognitive Alignment & Resistance Simulator) models a client whose resistance
emerges dynamically from Cognitive Conceptualization Diagrams (CCDs) rather than
being scripted. Each turn, the client reasons over whether the counselor's strategy
triggers a resistance schema, updates its emotion, sets an interaction goal, and
generates a response conditioned on that state.

Key Features:
- Dual CCD structure: a stable main CCD plus a session-specific CCD of
  situation-dependent automatic thoughts and resistance triggers
- Structured resistance reasoning: topic -> schema trigger -> strategy-consistency
  check -> emotion/goal update -> nonverbal cue + response
- Dynamic emotion state (0-100); extremely low emotion ends the session
- Preferred counselor style and client characteristics modulate cooperation

Note: the paper's response step (§3.1.2) selects sentence patterns from a
"pre-defined emotion-utterance corpus." The authors do not publish that corpus,
so it is intentionally omitted here rather than fabricated.
"""

import logging
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.utils import flatten_conv
from patienthub.schemas.cars import Response
from patienthub.configs import APIModelConfig

logger = logging.getLogger(__name__)


@dataclass
class CarsClientConfig(APIModelConfig):
    """Configuration for the CARS client agent."""

    agent_name: str = "cars"
    prompt_path: str = "data/prompts/client/cars.yaml"
    data_path: str = "data/characters/cars.json"
    data_idx: int = 0
    initial_emotion_state: int = 50
    termination_threshold: int = 10


class CarsClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.init_session_state(configs)
        super().__init__(configs)

    def init_session_state(self, configs: DictConfig) -> None:
        self.planning = ""
        self.session_ended = False
        self.turn_count = 0
        self.messages: list[dict[str, str]] = []
        self.emotion_state = configs.initial_emotion_state

    def build_sys_prompt(self):
        prompt = self.prompts["sys_prompt"].render(
            persona=self.data["persona"],
            background=self.data["background"],
            preference={
                "preferences": self.data["preferences"],
                "client_characteristics": self.data["client_characteristics"],
            },
            main_ccd=self.data["main_ccd"],
            secondary_ccd=self.data["session_ccd"],
            dialogue_history=flatten_conv(
                self.messages, roles={"user": "Therapist", "assistant": "Client"}
            ),
            planning=self.planning,
            emotion_state=self.emotion_state,
        )
        system_message = {"role": "system", "content": prompt}
        if self.messages:
            self.messages[0] = system_message
        else:
            self.messages = [system_message]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        self.build_sys_prompt()

        res = self.chat_model.generate(
            messages=[self.messages[0]],
            response_format=Response,
        )
        self.messages.append({"role": "assistant", "content": res.content})

        self.turn_count += 1
        self.planning = res.intention
        self.emotion_state = max(0, min(100, self.emotion_state + res.emotion))
        self.session_ended = self.emotion_state <= self.configs.termination_threshold

        logger.info(
            "CARS turn=%d emotion_delta=%d emotion_state=%d intention=%s "
            "nonverbal_behavior=%s response=%s",
            self.turn_count,
            res.emotion,
            self.emotion_state,
            res.intention,
            res.nonverbal_behavior,
            res.content,
        )
        if self.session_ended:
            logger.info(
                "CARS client terminating conversation: emotion_state=%d <= threshold=%d",
                self.emotion_state,
                self.configs.termination_threshold,
            )

        return res

    def reset(self) -> None:
        self.init_session_state(self.configs)
        super().reset()
