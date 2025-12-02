import json
import random
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from src.agents import InferenceAgent
from src.utils import load_json, load_prompts, get_model_client
from omegaconf import DictConfig
from langchain_core.messages import SystemMessage
from langchain_core.language_models import BaseChatModel


class Response(BaseModel):
    content: str = Field(
        description="Final response delivered to the therapist after self-revision."
    )


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


class RoleplayDohClient(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.model_client = get_model_client(configs)
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

    def generate(self, messages: List[Any], response_format: BaseModel):
        model = self.model_client.with_structured_output(response_format)
        res = model.invoke(messages)
        return res

    def generate_questions(
        self, principle: str, therapist_message: str, client_response: str
    ):
        prompt = self.prompts["question"].render(
            criteria=principle,
            therapist_message=therapist_message,
            client_response=client_response,
        )
        result = self.generate(
            [SystemMessage(content=prompt)], response_format=QuestionSet
        )
        questions = (result.questions or []) + (result.extra_questions or [])
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
        res = self.generate(
            [SystemMessage(content=prompt)], response_format=AssessmentResult
        )
        return res

    def generate_response(self, msg: str):
        self.messages.append({"role": "therapist", "content": msg})
        messages = [f"{msg['role']}: {msg['content']}" for msg in self.messages]

        # 1) Generate initial response
        response_pt = self.prompts["response"].render(
            profile=self.profile,
            conv_history="\n".join(messages),
        )
        initial_response = self.generate(
            [SystemMessage(content=response_pt)], response_format=Response
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
        if has_violation and revised_response:
            client_response = revised_response
        else:
            client_response = initial_response.content

        self.messages.append({"role": "client", "content": client_response})

        return Response(content=client_response)

    def reset(self):
        self.messages = []
        self.therapist = None
