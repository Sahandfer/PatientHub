import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .basic import BasicClient, ClientResponse

BACKEND_DIR = Path(__file__).resolve().parents[3]
ROLEPLAY_DIR = BACKEND_DIR / "roleplaydohClient"

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from roleplaydohClient import RoleplayDohPipeline  # type: ignore  # noqa: E402


class RoleplayDohClient(BasicClient):
    """Client agent enhanced with Roleplay-doh self-critique pipeline."""

    def __init__(
        self,
        model_client: BaseChatModel,
        data: Dict,
        principle_ids: Optional[List[str]] = None,
    ):
        base_ids = principle_ids or data.get("roleplay_principle_ids") or data.get(
            "roleplay_keys"
        )
        if isinstance(base_ids, str):
            base_ids = [base_ids]
        normalized_data = self._normalize_profile(data)
        super().__init__(model_client=model_client, data=normalized_data)
        verbose_flag = self._is_verbose_enabled()
        log_file = self._get_log_file_path()
        self.agent_type = "roleplaydoh"
        self.dialog_history: List[Dict[str, str]] = []
        self.therapist_name = "Therapist"
        self.original_profile = data
        self.persona = json.dumps(self.original_profile, ensure_ascii=False, indent=2)
        self.init_mental_state()
        prompt_file = ROLEPLAY_DIR / "prompts.yaml"
        principles_file = ROLEPLAY_DIR / "roleplay.json"
        self.pipeline = RoleplayDohPipeline(
            prompt_file=prompt_file,
            principles_file=principles_file,
            response_model=model_client,
            verbose=verbose_flag,
            log_file=log_file,
            context={
                "client_name": normalized_data.get("name"),
                "agent_type": "roleplaydoh",
                "principle_ids": base_ids,
            },
        )
        self.roleplay_principle_ids = base_ids
        self.verbose = verbose_flag
        self.log_file = log_file

    def set_therapist(
        self, therapist: Dict[str, str], prev_sessions: Optional[List[Dict[str, str]]] = None
    ):
        prev_sessions = prev_sessions or []
        demographics = None
        if isinstance(therapist, dict):
            self.therapist_name = therapist.get("name", self.therapist_name)
            demographics = therapist.get("demographics")
        else:
            self.therapist_name = getattr(therapist, "name", self.therapist_name)
            therapist_data = getattr(therapist, "data", None)
            if therapist_data:
                demographics = therapist_data.get("demographics")

        if demographics and "therapy" in self.prompts:
            self.messages[0].content += "\n" + self.prompts["therapy"].render(
                therapist=demographics, previous_sessions=prev_sessions
            )
        self.pipeline.update_context(therapist=self.therapist_name)

    def generate_response(self, msg: str):
        if len(self.messages) == 1:
            self.messages[0].content += "\n" + self.prompts["conversation"].render(
                data=self.data
            )

        normalized_msg = self._strip_speaker(msg)
        self.messages.append(HumanMessage(content=msg))
        self.dialog_history.append({"role": "Therapist", "content": normalized_msg})

        transcript = self._format_history()
        system_prompt = self.messages[0].content

        initial_response = self.pipeline.generate_initial_response(
            system_prompt=system_prompt, transcript=transcript
        )
        principles_map = self.pipeline.select_principles(self.roleplay_principle_ids)
        question_payload = self.pipeline.generate_questions(
            principles_map=principles_map,
            therapist_message=normalized_msg,
            client_response=initial_response,
        )
        selected_principle = question_payload.get("principle_id")
        if selected_principle:
            self.pipeline.update_context(selected_principle=selected_principle)
        combined_questions = (
            question_payload.get("questions", [])
            + question_payload.get("extra_questions", [])
        )
        if not combined_questions:
            combined_questions = [
                "Is the client's response consistent with the conversation history?"
            ]

        assessment = self.pipeline.assess_and_rewrite(
            question_list=combined_questions,
            persona=self.persona,
            conversation_history=transcript,
            therapist_message=normalized_msg,
            client_response=initial_response,
        )

        final_response = assessment.get("response") or initial_response
        reasoning = (
            assessment.get("reasoning")
            or "Roleplay-doh pipeline revision applied to ensure principle alignment."
        )

        self.dialog_history.append({"role": "Client", "content": final_response})

        client_response = ClientResponse(
            reasoning=reasoning,
            mental_state=self.mental_state,
            content=final_response.strip(),
        )
        self.messages.append(AIMessage(content=client_response.model_dump_json()))
        return client_response

    def reset(self):
        self.dialog_history = []
        profile = self.prompts["profile"].render(data=self.data)
        self.messages = [SystemMessage(content=profile)]
        self.init_mental_state()

    def _format_history(self) -> str:
        if not self.dialog_history:
            return ""
        return "\n".join(
            f"{entry['role']}: {entry['content']}".strip()
            for entry in self.dialog_history
        )

    def _strip_speaker(self, msg: str) -> str:
        candidates = [
            f"{self.therapist_name}: ",
            f"{self.name}: ",
            "Therapist: ",
            "Client: ",
            "咨询师: ",
            "来访者: ",
        ]
        for prefix in candidates:
            if msg.startswith(prefix):
                return msg[len(prefix) :].strip()
        return msg.strip()

    @staticmethod
    def _is_verbose_enabled() -> bool:
        env_value = os.getenv("ROLEPLAYDOH_VERBOSE", "")
        return env_value.lower() in {"1", "true", "on", "yes"}

    @staticmethod
    def _get_log_file_path() -> Optional[Path]:
        log_path = os.getenv("ROLEPLAYDOH_LOG", "").strip()
        return Path(log_path) if log_path else None

    @staticmethod
    def _normalize_profile(raw: Dict) -> Dict:
        if raw.get("demographics") and raw.get("current_issue"):
            return raw

        name = raw.get("name") or raw.get("demographics", {}).get("name") or "Client"

        def _split_items(value: Optional[str | List[str]]) -> List[str]:
            if isinstance(value, list):
                return [str(item).strip() for item in value if str(item).strip()]
            if isinstance(value, str):
                parts = re.split(r"[.;]\s+", value)
                return [part.strip(" .") for part in parts if part.strip(" .")]
            return []

        coping_items = _split_items(raw.get("coping_strategies"))
        if not coping_items:
            coping_items = ["Not specified coping strategy"]

        triggers = [
            text.strip()
            for text in [
                raw.get("situation", ""),
                raw.get("auto_thought", ""),
                raw.get("behavior", ""),
            ]
            if isinstance(text, str) and text.strip()
        ] or ["Unclear stressors"]

        demographics = {
            "name": name,
            "age": raw.get("age", "Unknown"),
            "gender": raw.get("gender", "Unknown"),
            "ethnicity": raw.get("ethnicity", "Unknown"),
            "location": raw.get("location", "Unknown"),
            "income": raw.get("income", "Unknown"),
            "marital_status": raw.get("marital_status", "Unknown"),
            "occupation": {
                "status": raw.get("occupation_status", "Unknown"),
                "title": raw.get("occupation_title", "Unknown"),
                "company": raw.get("occupation_company", "Unknown"),
                "industry": raw.get("occupation_industry", "Unknown"),
            },
        }

        description_source = (
            raw.get("history")
            or raw.get("helpless_belief_current")
            or raw.get("intermediate_belief")
            or "Ongoing personal struggles."
        )
        if isinstance(description_source, list):
            description_text = "; ".join(
                str(item) for item in description_source if str(item).strip()
            )
        else:
            description_text = str(description_source)

        current_issue = {
            "description": description_text,
            "duration": raw.get("issue_duration", "some time"),
            "triggers": triggers,
            "coping_mechanisms": [
                {"name": item, "type": "Unknown"} for item in coping_items
            ],
        }

        normalized = dict(raw)
        normalized["name"] = name
        normalized["demographics"] = demographics
        normalized["personality"] = {
            "description": raw.get("history", "No background provided."),
        }
        normalized["social_circle"] = raw.get("social_circle", [])
        normalized["current_issue"] = current_issue
        return normalized
