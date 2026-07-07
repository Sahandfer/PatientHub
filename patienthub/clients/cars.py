import json
import logging
from dataclasses import dataclass
from typing import Any

from omegaconf import DictConfig

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.schemas.cars import CarsResponseState
from patienthub.utils import flatten_conv

logger = logging.getLogger(__name__)


@dataclass
class CarsClientConfig(APIModelConfig):
    """Configuration for the CARS client agent."""

    agent_name: str = "cars"
    prompt_path: str = "data/prompts/client/cars.yaml"
    data_path: str = "data/characters/cars.json"
    data_idx: int = 0


class CarsClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.emotion_state = 50
        self.planning = ""
        self.last_nonverbal_behavior = ""
        self.cars_trace: list[CarsResponseState] = []
        self._cars_state_initialized = False
        super().__init__(configs)

    def initialize_cars_state(self) -> None:
        if self._cars_state_initialized:
            return
        self.emotion_state = int(self.data.get("initial_emotion_state", 50))
        self.planning = ""
        self.last_nonverbal_behavior = ""
        self.cars_trace = []
        self._cars_state_initialized = True

    @staticmethod
    def json_dump(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2)

    def dialogue_history(self) -> str:
        return flatten_conv(
            getattr(self, "messages", []),
            roles={"user": "Therapist", "assistant": "Client"},
        )

    def render_system_prompt(self) -> str:
        self.initialize_cars_state()
        prompt_data = {
            "persona": self.json_dump(self.data["persona"]),
            "background": self.data.get("background", ""),
            "preference": self.json_dump(
                {
                    "preferences": self.data.get("preferences", {}),
                    "client_characteristics": self.data.get(
                        "client_characteristics", {}
                    ),
                }
            ),
            "main_ccd": self.json_dump(
                self.data.get("main_cognitive_conceptualization_diagram", {})
            ),
            "secondary_ccd": self.json_dump(
                self.data.get(
                    "session_specific_cognitive_conceptualization_diagram", {}
                )
            ),
            "example": self.json_dump(
                {
                    "emotion_utterance_examples": self.data.get(
                        "emotion_utterance_examples", []
                    ),
                    "example_interaction": self.data.get("example_interaction", {}),
                    "example_state_update": self.data.get("example_state_update", {}),
                }
            ),
            "dialogue_history": self.dialogue_history(),
            "planning": self.planning,
            "emotion_state": self.emotion_state,
        }
        return self.prompts["sys_prompt"].render(**prompt_data)

    def build_sys_prompt(self):
        prompt = self.render_system_prompt()
        system_message = {"role": "system", "content": prompt}
        if not getattr(self, "messages", None):
            self.messages = [system_message]
        elif self.messages[0].get("role") == "system":
            self.messages[0] = system_message
        else:
            self.messages.insert(0, system_message)

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        self.build_sys_prompt()

        state = self.chat_model.generate(
            messages=[self.messages[0]],
            response_format=CarsResponseState,
        )

        self.emotion_state = max(0, min(100, self.emotion_state + state.emotion))
        self.planning = state.intention
        self.last_nonverbal_behavior = state.nonverbal_behavior
        self.cars_trace.append(state)
        logger.info(
            "CARS turn=%d emotion_delta=%d emotion_state=%d intention=%s "
            "nonverbal_behavior=%s response=%s",
            len(self.cars_trace),
            state.emotion,
            self.emotion_state,
            state.intention,
            state.nonverbal_behavior,
            state.response,
        )

        self.messages.append({"role": "assistant", "content": state.response})
        return state.response

    def reset(self) -> None:
        self._cars_state_initialized = False
        self.messages = []
        super().reset()
