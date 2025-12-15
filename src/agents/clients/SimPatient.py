import random
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from src.agents import InferenceAgent
from src.utils import get_model_client, load_json, load_prompts, save_json

from omegaconf import DictConfig
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    get_buffer_string,
)


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


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


class SimPatientClient(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        # Profile and cognitive model configuration
        self.data: Dict[str, Any] = load_json(configs.data_path)
        self.persona: Dict[str, Any] = self.data.get("persona", {})
        self.cognitive_model_values: Dict[str, int] = self.data.get(
            "cognitive_model_values", {}
        )
        # Will be initialized or regenerated based on session logic
        self.between_session_event: str | None = None

        self.name = "SimPatient"

        # Conversation configuration
        self.continue_last_session: bool = bool(
            getattr(configs, "continue_last_session", False)
        )
        self.conversation_history_path: str | None = getattr(
            configs, "conversation_history", None
        )

        self.model_client = get_model_client(configs)
        self.prompts = load_prompts(
            role="client", agent_type="SimPatient", lang=configs.lang
        )

        # In-session messages for this run (Therapist/Client turns)
        self.messages: List[Any] = []
        self.past_session_history: str = ""

        self.therapist: str | None = None

        self.init_session_state()

    def generate(self, messages: List[Any], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_therapist(
        self,
        therapist: Dict[str, Any],
        prev_sessions: List[Dict[str, str]] | None = None,
    ):
        self.therapist = therapist.get("name", "Therapist")

    def generate_response(self, msg: str):
        # Append current therapist utterance to in-session history
        self.messages.append(HumanMessage(content=msg))

        current_session_history = get_buffer_string(
            self.messages,
            human_prefix="Therapist",
            ai_prefix="Client",
        )

        prompt = self.prompts["patient_response_prompt"].render(
            persona=self.persona,
            cognitive_model=self.cognitive_model_values,
            past_session_history=self.past_session_history,
            between_session_event=self.between_session_event or "",
            current_session_history=current_session_history,
            counselor_input=msg,
        )

        res = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=Response,
        )

        patient_text = res.content.strip()
        self.messages.append(AIMessage(content=patient_text))

        self.update_internal_state(
            therapist_message=msg,
            patient_response=patient_text,
        )

        return res

    def reset(self):
        self.data = load_json(self.configs.data_path)
        self.persona = self.data.get("persona", {})
        self.cognitive_model_values = self.data.get("cognitive_model_values", {})
        self.between_session_event = None

        self.messages = []
        self.past_session_history = ""
        self.therapist = None

        self.init_session_state()

    def init_session_state(self):
        """Initialize session state, optionally continuing from a previous session."""
        if not (self.continue_last_session and self.conversation_history_path):
            self.init_random_cognitive_model()
            return

        try:
            session_data = load_json(self.conversation_history_path)
        except Exception:
            self.init_random_cognitive_model()
            return

        messages = session_data.get("messages") or []
        if not messages:
            self.init_random_cognitive_model()
            return

        self.past_session_history = "\n".join(
            f"{m.get('role', '')}: {m.get('content', '')}" for m in messages
        )
        self.generate_between_session_event(self.past_session_history)

    def init_random_cognitive_model(self):
        """Randomly initialize cognitive model values when starting a new trajectory."""
        self.cognitive_model_values = {
            "patient_control": random.randint(1, 10),
            "patient_efficacy": random.randint(1, 10),
            "patient_awareness": random.randint(1, 10),
            "patient_reward": random.randint(1, 10),
        }
        self.data["cognitive_model_values"] = self.cognitive_model_values
        self.between_session_event = None
        save_json(self.data, self.configs.data_path)

    def generate_between_session_event(self, session_history: str):
        """Generate a between-session event from previous session history."""
        prompt = self.prompts["between_session_event_prompt"].render(
            persona=self.persona,
            cognitive_model=self.cognitive_model_values,
            session_history=session_history,
        )

        res = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=Response,
        )

        self.between_session_event = res.content.strip()
        self.data["between_session_event"] = self.between_session_event
        save_json(self.data, self.configs.data_path)

    def update_internal_state(self, therapist_message: str, patient_response: str):
        """Update internal cognitive model based on the latest interaction."""
        session_history = get_buffer_string(
            self.messages,
            human_prefix="Therapist",
            ai_prefix="Client",
        )

        prompt = self.prompts["update_internal_state_prompt"].render(
            cognitive_model=self.cognitive_model_values,
            session_history=session_history,
            counselor_input=therapist_message,
            patient_response=patient_response,
        )

        res = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=InternalStateResponse,
        )

        self.cognitive_model_values = {
            "patient_control": res.patient_control,
            "patient_efficacy": res.patient_efficacy,
            "patient_awareness": res.patient_awareness,
            "patient_reward": res.patient_reward,
        }
        self.data["cognitive_model_values"] = self.cognitive_model_values
        save_json(self.data, self.configs.data_path)
