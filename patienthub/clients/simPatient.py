# coding=utf-8
# Licensed under the MIT License;

"""SimPatient Client - Cognitive model-based patient with dynamic state updates.

Paper: "Scaffolding Empathy: Training Counselors with Simulated Patients and
       Utterance-level Performance Visualizations" (CHI 2025)
       https://dl.acm.org/doi/full/10.1145/3706598.3714014

SimPatient models patients dealing with alcohol misuse using an evolving cognitive
model.

Key Features:
- 4 internal states (1-10 scale): control, efficacy, awareness, reward
- Dynamic state updates based on therapist interactions
- Between-session event generation for multi-session continuity
- Designed for Motivational Interviewing training
"""

import random
from typing import Dict
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import get_chat_model, load_json, load_prompts


@dataclass
class SimPatientClientConfig(APIModelConfig):
    """Configuration for SimPatient client agent."""

    agent_type: str = "simPatient"
    prompt_path: str = "data/prompts/client/simPatient.yaml"
    data_path: str = "data/characters/SimPatient.json"
    conv_history_path: str = "data/sessions/SimPatient/session_1.json"
    data_idx: int = 0
    continue_last_session: bool = False


class InternalStateResponse(BaseModel):
    patient_control: int = Field(
        description="Updated control level (1-10 scale)",
        ge=1,
        le=10,
    )
    patient_efficacy: int = Field(
        description="Updated self-efficacy level (1-10 scale)",
        ge=1,
        le=10,
    )
    patient_awareness: int = Field(
        description="Updated awareness level (1-10 scale)",
        ge=1,
        le=10,
    )
    patient_reward: int = Field(
        description="Updated reward level (1-10 scale)",
        ge=1,
        le=10,
    )
    reasoning: str = Field(
        description="Single reasoning for all updated values",
    )


class SimPatientClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.data = load_json(configs.data_path)
        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)

        self.build_sys_prompt()

    def load_cognitive_model(self, prev_cognitive_model: Dict[str, int] | None = None):
        cognitive_model = prev_cognitive_model or self.data.get("cognitive_model", {})
        if not cognitive_model:
            cognitive_model = {
                "patient_control": random.randint(1, 10),
                "patient_efficacy": random.randint(1, 10),
                "patient_awareness": random.randint(1, 10),
                "patient_reward": random.randint(1, 10),
            }
        self.cognitive_model = self.prompts["cognitive_model"].render(
            cognitive_model=cognitive_model, data=cognitive_model
        )

    def generate_between_session_event(self, session_history: str):
        """Generate a between-session event from previous session history."""
        prompt = self.prompts["between_session_event"].render(
            profile=self.profile,
            cognitive_model=self.cognitive_model,
            session_history=session_history,
        )

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
        )

        self.between_session_event = res.content.strip()
        self.data["between_session_event"] = self.between_session_event

    def build_sys_prompt(self):
        """Initialize session state, optionally continuing from a previous session."""
        profile_data = self.data.get("persona", {})
        self.profile = self.prompts["profile"].render(persona=profile_data)
        # Load from a previous conversation
        if self.configs.continue_last_session:
            try:
                session_data = load_json(self.configs.conv_history_path)
                messages = session_data.get("messages", [])
                self.prev_session_history = "\n".join(
                    f"{m.get('role', '')}: {m.get('content', '')}" for m in messages
                )
                self.past_session_history = self.prev_session_history
                self.generate_between_session_event(self.prev_session_history)
                cognitive_model = session_data.get("data", {}).get(
                    "cognitive_model", {}
                )
                self.load_cognitive_model(prev_cognitive_model=cognitive_model)
            except Exception:
                self.prev_session_history = ""
                self.past_session_history = ""
                self.between_session_event = None
                self.load_cognitive_model()
        else:
            self.load_cognitive_model()
            self.between_session_event = None
        self.messages = []

    def update_internal_state(self, therapist_message: str, patient_response: str):
        """Update internal cognitive model based on the latest interaction."""
        session_history = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in self.messages
        )

        prompt = self.prompts["update_internal_state"].render(
            cognitive_model=self.cognitive_model,
            session_history=session_history,
            counselor_input=therapist_message,
            patient_response=patient_response,
        )

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=InternalStateResponse,
        )

        self.cognitive_model = {
            "patient_control": res.patient_control,
            "patient_efficacy": res.patient_efficacy,
            "patient_awareness": res.patient_awareness,
            "patient_reward": res.patient_reward,
        }
        self.data["cognitive_model"] = self.cognitive_model

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})

        current_session_history = "\n".join(
            f"{'Therapist' if m['role'] == 'user' else 'Client'}: {m['content']}"
            for m in self.messages
            if m["role"] in ["user", "assistant"]
        )

        prompt = self.prompts["response"].render(
            persona=self.profile,
            cognitive_model=self.cognitive_model,
            past_session_history=self.past_session_history,
            between_session_event=self.between_session_event or "",
            current_session_history=current_session_history,
            counselor_input=msg,
        )

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
        ).content.strip()

        self.messages.append({"role": "assistant", "content": res})

        self.update_internal_state(
            therapist_message=msg,
            patient_response=res,
        )

        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
