# coding=utf-8
# Licensed under the MIT License;

"""AdaptiveVP Client - Virtual patient for nurse communication training.

Paper: "A Framework for LLM-Based Virtual Patients that Adapts to Trainees'
       Dialogue to Facilitate Nurse Communication Training" (ACL 2025 Findings)
       https://aclanthology.org/2025.findings-acl.118/

AdaptiveVP creates virtual patients that adapt their responses based on the
trainee's communication quality. The workflow:

1. Analyze nurse input on tone (calm/clear), empathy (0-6), and de-escalation
2. Select stage direction based on analysis results
3. Generate response with inner monologue, verbal content, and non-verbal cues
4. Safety monitoring to ensure responses stay within professional boundaries (if necessary)

Patient types: Dependent, Authoritarian, Aggressive, Uncooperative
"""

from typing import Literal
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class AdaptiveVPClientConfig(APIModelConfig):
    """
    Configuration for the AdaptiveVPClient agent.
    """

    agent_type: str = "adaptiveVP"
    prompt_path: str = "data/prompts/client/adaptiveVP.yaml"
    data_path: str = "data/characters/AdaptiveVP.json"
    directions_path: str = "data/resources/AdaptiveVP_stage_direction.json"
    data_idx: int = 0


class ToneAssessment(BaseModel):
    calm: Literal["yes", "no"] = Field(
        description="Whether the nurse's tone was calm. Assess if the nurse sufficiently suppressed contempt, frustration, anger, or anxiety."
    )
    clear: Literal["yes", "no"] = Field(
        description="Whether the nurse's tone was clear. Assess if the nurse used clear sentences to reduce confusion or prevent escalation."
    )
    explanation: str = Field(
        description="A brief explanation of the tone assessment in 1-2 sentences."
    )


class EmpathyEvaluation(BaseModel):
    level: int = Field(description="Empathy level on a scale from 0 to 6.", ge=0, le=6)
    explanation: str = Field(
        description="A brief explanation of the empathy level assessment in 1-2 sentences."
    )


class DeescalationAspect(BaseModel):
    used: Literal["yes", "no"] = Field(
        description="Whether the patient exercised this aspect in their response."
    )
    explanation: str = Field(
        description="A brief explanation of the assessment in 1-2 sentences."
    )


class DeescalationTechniques(BaseModel):
    autonomy: DeescalationAspect = Field(
        description="Did the nurse involve the patient in decision-making, offer options, or use techniques like seeking permission or providing emotional space? e.g. 'We can proceed with either X or Y—what do you prefer?', 'Would it be okay if we talk about this further after you've had a moment to think?'"
    )
    limit_setting: DeescalationAspect = Field(
        description="Did the nurse establish clear behavioral boundaries or explain consequences? e.g. 'I understand you're upset, but I cannot allow yelling during this conversation.', 'If this continues, I may need to step away for a moment until we can discuss this calmly.'"
    )
    problem_solving_and_reframing: DeescalationAspect = Field(
        description="Did the nurse clarify the issue, redirect focus, or encourage a broader perspective? e.g. 'It seems like you're feeling frustrated because you've been waiting for a long time—am I understanding that correctly?', 'I know this feels overwhelming, but remember, your family is looking forward to seeing you healthy again.'"
    )


class ProhibitedBehavior(BaseModel):
    premature_empathy: Literal["yes", "no"] = Field(
        description="Did the nurse avoid phrases like 'I understand' unless fully justified."
    )
    invalidating_beliefs: Literal["yes", "no"] = Field(
        description="did the nurse avoid dismissing the patient's feelings or beliefs as untrue."
    )
    dismissive_commands: Literal["yes", "no"] = Field(
        description="did the nurse phrases like 'Calm down,' which can escalate emotions."
    )
    explanation: str = Field(
        description="A brief explanation of the prohibited behavior assessment in 1-2 sentences."
    )


class Analysis(BaseModel):
    tone: ToneAssessment = Field()
    empathy: EmpathyEvaluation = Field()
    deescalation: DeescalationTechniques = Field()
    prohibited_behavior: ProhibitedBehavior = Field()


class Response(BaseModel):
    inner_monologue: str = Field(
        description="The patient's internal thoughts and reactions to the nurse's response."
    )
    content: str = Field(
        description="The patient's actual verbal response to the nurse."
    )
    non_verbal: str = Field(
        description="Any non-verbal communication or actions that you as the patient would take."
    )


class EvaluationAspect(BaseModel):
    judge: bool = Field(description="Whether the response adheres to this aspect.")
    explanation: str = Field(
        description="A brief explanation of this assessment in 1-2 sentences."
    )


class Evaluation(BaseModel):
    profile_alignment: EvaluationAspect = Field(
        description="Whether the response aligns with the patient's profile"
    )
    direction_adherence: EvaluationAspect = Field(
        description="Whether the response adheres to the provided direction"
    )
    dialogue_effectiveness: EvaluationAspect = Field(
        description="Whether the response is effective for training the nurse"
    )
    nurse_safety: EvaluationAspect = Field(
        description="Whether the response ensures the safety of the nurse"
    )


class AdaptiveVPClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.directions = load_json(configs.directions_path)
        self.name = self.data.get("name", "client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)

    def build_sys_prompt(self):
        self.profile = "\n".join(
            f"{k}: {v}"
            for k, v in self.data.items()
            if k not in {"id", "type", "first_statement"}
        )
        self.messages = []

    def get_conv_str(self) -> str:
        """Get conversation history as string"""
        return "\n".join(
            f"{'Client' if msg['role'] == 'assistant' else 'Nurse'}: {msg['content']}"
            for msg in self.messages
            if msg["role"] != "system"
        )

    # For brevity, we only include one agent's evaluation (the original paper uses multi-agent evaluation and their consensus as the final result)
    def calc_eval_score(self, eval_res: Analysis) -> int:

        tone_score = (
            1 if eval_res.tone.calm == "yes" and eval_res.tone.clear == "yes" else 0
        )
        empathy_score = 1 if eval_res.empathy.level >= 3 else 0
        deescalation_score = sum(
            k.used == "yes" for k in eval_res.deescalation.__dict__.values()
        )
        prohibited_behavior_score = (
            -1
            if any(
                v == "no"
                for k, v in eval_res.prohibited_behavior.__dict__.items()
                if k != "explanation"
            )
            else 0
        )

        return (
            tone_score + empathy_score + deescalation_score + prohibited_behavior_score
        )

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})

        # Step 1: Determine the patient's response direction based on the nurse's message
        prompt = self.prompts["evaluate"].render(
            patient_profile=self.profile, conv_history=self.get_conv_str()
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=Analysis
        )
        score = self.calc_eval_score(res)
        direction = self.directions[score]

        # Step 2: Generate a response based on the determined direction

        prompt = self.prompts["chat"].render(
            patient_profile=self.profile,
            direction=direction,
            conv_history=self.get_conv_str(),
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=Response
        )
        self.messages.append({"role": "assistant", "content": res.content})

        # Step 3: Evaluate the safety of the generated response (if necessary)
        # prompt = self.prompts["safety"].render(
        #     patient_profile=self.profile,
        #     direction=direction,
        #     conv_history=self.get_conv_str(),
        # )

        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
