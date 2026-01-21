import json
import random
from omegaconf import DictConfig
from dataclasses import dataclass
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, load_prompts, get_chat_model


@dataclass
class RoleplayDohClientConfig(APIModelConfig):
    """Configuration for RoleplayDoh client agent."""

    agent_type: str = "roleplayDoh"
    data_path: str = "data/characters/PatientPsi.json"
    principles: str = "data/resources/roleplayDohPrinciple.json"
    data_idx: int = 0


class QuestionSet(BaseModel):
    questions: List[str] = Field(
        default_factory=list,
        description="1a and 1b, the list of all questions generated",
    )
    extra_questions: List[str] = Field(
        default_factory=list,
        description="2a and 2b,the list of all additional criteria generated. Do not enforce any beliefs about how the client or therapist should behave when generating these criteria.",
    )
    extra_questions_justification: List[str] = Field(
        default_factory=list, description="2c, justify additional criteria."
    )


class AssessmentResult(BaseModel):
    answers: List[str] = Field(
        default_factory=list, description="list of answers to the criteria questions"
    )
    justification: List[str] = Field(
        default_factory=list, description="list of justification for your answers"
    )
    response: str = Field(
        default="",
        description="new response. This response should not start with a greeting like 'Hi' if there is prior conversation history.",
    )
    reasoning: str = Field(
        default="",
        description="justify the new response and why it is not a paraphrase of the original response. You are allowed to deviate significantly from the original response while generating the new response.",
    )


class RoleplayDohClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="roleplayDoh", lang=configs.lang
        )

        self.profile = json.dumps(self.data, ensure_ascii=False, indent=2)
        self.principles = self.load_principles()
        self.messages = []

    def load_principles(self):
        principles_map = load_json(self.configs.principles)
        principles: List[str] = []
        for group in principles_map.values():
            principles.extend(group)
        if not principles:
            principles.append(
                "Ensure the response is authentic, relevant, and aligned with the client's persona."
            )
        return principles

    def set_therapist(
        self,
        therapist: Dict[str, Any],
        prev_sessions: List[Dict[str, str]] | None = None,
    ):
        self.therapist = therapist.get("name", "Therapist")

    def generate_questions(
        self, principle: str, therapist_message: str, client_response: str
    ):
        prompt = self.prompts["question"].render(
            criteria=principle,
            therapist_message=therapist_message,
            client_response=client_response,
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=QuestionSet
        )
        questions = (res.questions or []) + (res.extra_questions or [])
        if not questions:
            questions = [
                "Is the client's response relevant and consistent with the therapist's latest message?"
            ]
        return questions

    def generate_assessment(
        self,
        questions: List[str],
        therapist_message: str,
        response: str,
    ):
        criteria_lines = "\n".join(f"- {q}" for q in questions)
        prompt = self.prompts["assessment"].render(
            criteria=criteria_lines,
            profile=self.profile,
            conv_history=[],
            therapist_message=therapist_message,
            client_response=response,
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=AssessmentResult
        )
        return res

    def generate_response(self, msg: str):
        self.messages.append({"role": "therapist", "content": msg})

        # 1) Generate initial response
        response_pt = self.prompts["response"].render(
            profile=self.profile,
            conv_history="\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in self.messages]
            ),
        )
        initial_response = self.chat_model.generate(
            [{"role": "system", "content": response_pt}]
        )

        # 2) Generate questions

        # TODO: Find a better way to select principle
        principle = random.choice(self.principles)
        questions = self.generate_questions(principle, msg, initial_response.content)

        # 3) Generate assessment
        assessment = self.generate_assessment(questions, msg, initial_response.content)

        # 4) Revise and finalize the response
        has_violation = any(
            ans.strip().lower().startswith("no") for ans in assessment.answers
        )
        revised_response = assessment.response.strip()

        response = (
            revised_response
            if has_violation and revised_response
            else initial_response.content
        )

        self.messages.append({"role": "client", "content": response})

        return response

    def reset(self):
        self.messages = []
        self.therapist = None
