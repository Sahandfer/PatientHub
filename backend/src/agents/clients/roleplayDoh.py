import json
import random
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ConfigDict

from ..base import BaseAgent
from utils import load_json, load_prompts


class RoleplayDohResponse(BaseModel):
    content: str = Field(
        description="Final response delivered to the therapist after self-revision."
    )


class QuestionSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    questions: List[str] = Field(default_factory=list)
    extra_questions: List[str] = Field(
        default_factory=list, alias="extra questions"
    )
    extra_questions_justification: List[str] = Field(default_factory=list)


class QuestionGenerationOutput(BaseModel):
    result: QuestionSet


class AssessmentResult(BaseModel):
    answers: List[str] = Field(default_factory=list)
    justification: List[str] = Field(default_factory=list)
    response: str = Field(default="")
    reasoning: str = Field(default="")


class AssessmentOutput(BaseModel):
    result: AssessmentResult


class RoleplayDohClient(BaseAgent):
    def __init__(
        self,
        model_client: BaseChatModel,
        data: Dict[str, Any],
        lang: str = "en",
    ):
        self.role = "client"
        self.agent_type = "roleplayDoh"
        self.lang = lang
        self.data = data
        self.name = data.get("name", "Client")
        self.model_client = model_client
        self.prompts = load_prompts(
            role=self.role, agent_type=self.agent_type, lang=self.lang
        )
        self.client_profile = json.dumps(self.data, ensure_ascii=False, indent=2)
        self.principles = self._load_principles()
        self.therapist_name: Optional[str] = None
        self.history: List[Dict[str, str]] = []
        self.messages = [
            SystemMessage(
                content=(
                    f"You are roleplaying as {self.name}. "
                    "Adhere to the provided persona and keep responses grounded in it."
                )
            )
        ]

    def _load_principles(self) -> List[str]:
        principles_map = load_json("data/characters/roleplayDohPrinciple.json")
        principles: List[str] = []
        for group in principles_map.values():
            principles.extend(group)
        if not principles:
            principles.append(
                "Ensure the response is authentic, relevant, and aligned with the client's persona."
            )
        return principles

    def set_therapist(
        self, therapist: Dict[str, Any], prev_sessions: List[Dict[str, str]] | None = None
    ):
        self.therapist_name = therapist.get("name", "Therapist")

    def generate(
        self, messages: List[Any], response_format: Optional[type[BaseModel]] = None
    ):
        if response_format:
            model = self.model_client.with_structured_output(response_format)
        else:
            model = self.model_client
        return model.invoke(messages)

    def _format_history(
        self,
        additional: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        turns = self.history + (additional or [])
        if not turns:
            return "No prior conversation."
        lines: List[str] = []
        therapist_label = self.therapist_name or "Therapist"
        for turn in turns:
            speaker = therapist_label if turn["role"] == "therapist" else self.name
            lines.append(f"{speaker}: {turn['content']}")
        return "\n".join(lines)

    def _strip_therapist_prefix(self, msg: str) -> str:
        prefix = f"{self.therapist_name}: " if self.therapist_name else None
        if prefix and msg.startswith(prefix):
            return msg[len(prefix) :]
        return msg

    def _select_principle(self) -> str:
        return random.choice(self.principles)

    def _generate_initial_response(self, therapist_message: str) -> str:
        prompt = self.prompts["Initial_Response_Prompt"].render(
            client_profile=self.client_profile,
            conversation_history=self._format_history(
                additional=[{"role": "therapist", "content": therapist_message}]
            ),
        )
        response = self.generate([HumanMessage(content=prompt)])
        return response.content.strip()

    def _generate_questions(
        self, principle: str, therapist_message: str, client_response: str
    ) -> List[str]:
        prompt = self.prompts["Question_Rewrite_Prompt"].render(
            criteria_payload=principle,
            therapist_message=therapist_message,
            client_response=client_response,
        )
        result: QuestionGenerationOutput = self.generate(
            [HumanMessage(content=prompt)], response_format=QuestionGenerationOutput
        )
        questions = (result.result.questions or []) + (
            result.result.extra_questions or []
        )
        if not questions:
            questions = [
                "Is the client's response relevant and consistent with the therapist's latest message?"
            ]
        return questions

    def _assess_response(
        self,
        questions: List[str],
        therapist_message: str,
        initial_response: str,
    ) -> AssessmentResult:
        criteria_lines = "\n".join(f"- {q}" for q in questions)
        prompt = self.prompts["Assess_Revise_Prompt"].render(
            criteria_lines=criteria_lines,
            persona=self.client_profile,
            conversation_history=self._format_history(),
            therapist_message=therapist_message,
            client_response=initial_response,
        )
        result: AssessmentOutput = self.generate(
            [HumanMessage(content=prompt)], response_format=AssessmentOutput
        )
        return result.result

    def _finalize_response(
        self, initial_response: str, assessment: AssessmentResult
    ) -> str:
        has_violation = any(
            ans.strip().lower().startswith("no") for ans in assessment.answers
        )
        revised = assessment.response.strip()
        if has_violation and revised:
            return revised
        return initial_response

    def generate_response(self, msg: str):
        therapist_message = self._strip_therapist_prefix(msg)
        self.messages.append(HumanMessage(content=msg))

        initial_response = self._generate_initial_response(therapist_message)
        principle = self._select_principle()
        questions = self._generate_questions(
            principle, therapist_message, initial_response
        )
        assessment = self._assess_response(questions, therapist_message, initial_response)
        final_response = self._finalize_response(initial_response, assessment)

        self.history.append({"role": "therapist", "content": therapist_message})
        self.history.append({"role": "client", "content": final_response})
        self.messages.append(AIMessage(content=final_response))

        return RoleplayDohResponse(content=final_response)

    def reset(self):
        self.history.clear()
        self.messages = [
            SystemMessage(
                content=(
                    f"You are roleplaying as {self.name}. "
                    "Adhere to the provided persona and keep responses grounded in it."
                )
            )
        ]
        self.therapist_name = None
