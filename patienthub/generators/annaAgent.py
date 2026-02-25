# coding=utf-8
# Licensed under the MIT License;

"""AnnaAgent Generator - Creates multi-session client profiles with memory structures.

Generates character files for the AnnaAgent client method, supporting longitudinal
therapy simulations.

Key Features:
- Multi-session support with evolving memory states
- Risk level assessment (depression/suicide)
- Complaint chain progression through cognitive change stages
- GoEmotions-based emotional profile generation
- Scale-based assessments (PHQ-9, GAD-7, etc.)
"""

import random
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal, List

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.utils import (
    load_prompts,
    get_chat_model,
    load_json,
    load_csv,
    save_json,
)


@dataclass
class AnnaAgentGeneratorConfig(APIModelConfig):
    """Configuration for AnnaAgent generator."""

    agent_type: str = "annaAgent"
    prompt_path: str = "data/prompts/generator/annaAgent.yaml"
    input_dir: str = "data/resources/AnnaAgent"
    output_dir: str = "data/characters/AnnaAgent.json"


class ScaleAnswer(BaseModel):
    """Response for scale answers (general)"""

    answers: List[Literal["A", "B", "C", "D"]] = Field(
        description="Array of scale answers, each item is A/B/C/D"
    )


class ComplaintNode(BaseModel):
    stage: int = Field(description="Stage number in the complaint change chain")
    content: str = Field(description="Content of the complaint at this stage")


class ComplaintChainResponse(BaseModel):
    chain: List[ComplaintNode] = Field(
        description="Cognitive change chain of the chief complaint, containing 3-7 stages",
        min_length=3,
        max_length=7,
    )


class SituationResponse(BaseModel):
    """Response for situational description"""

    situation: str = Field(
        description="Second-person description of the patient's current situation"
    )


class StyleResponse(BaseModel):
    """Response for speaking style analysis"""

    style: List[str] = Field(
        description="Patient's speaking style characteristics, 1-5 items",
        min_length=1,
        max_length=5,
    )


class ChangeItem(BaseModel):
    """Response for scale change items"""

    item: str = Field(description="Content or number of the item")
    change: Literal["Improved", "Worsened", "No Change"] = Field(
        description="Type of change"
    )
    explanation: str = Field(description="Explanation of the change")


class ScaleChangesResponse(BaseModel):
    """Response for scale change analysis"""

    changes: List[ChangeItem] = Field(
        description="Analysis of changes for each item in the scale"
    )
    summary: str = Field(description="Summary of overall change trends")


class StatusResponse(BaseModel):
    """Response for status summary"""

    status: str = Field(
        description="Summary of the patient's current overall psychological state"
    )


class AnnaAgentCharacter(BaseModel):
    profile: Dict[str, Any] = Field(description="Patient profile information")
    situation: str = Field(description="Current situation description")
    statement: List[str] = Field(description="Patient's statement")
    style: List[str] = Field(description="Patient's speaking style characteristics")
    complaint_chain: List[Dict[Any, Any]] = Field(
        description="Cognitive change chain of the chief complaint"
    )
    status: str = Field(description="Summary of the patient's current status")
    report: Dict[str, Any] = Field(
        description="Generated psychological assessment report"
    )
    previous_conversations: List[Dict[Any, Any]] = Field(
        default=None, description="Previous conversation history"
    )


class AnnaAgentGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(self.configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)

        input_dir = self.configs.input_dir
        self.data = load_json(f"{input_dir}/case.json")
        self.profile = self.data.get("profile", {})
        self.profile_str = self.prompts["profile"].render(profile=self.profile)
        self.report = self.data.get("report", "")
        self.prev_conv = self.data.get("previous_conversations", [])
        self.prev_conv_str = "\n".join(
            [f"{conv['role']}: {conv['content']}" for conv in self.prev_conv]
        )
        self.adult_events = load_csv(f"{input_dir}/adult_events.csv")
        self.teen_events = load_json(f"{input_dir}/teen_events.json")[self.configs.lang]
        self.scales = load_json(f"{input_dir}/scales.json")

    def fill_scale(
        self,
        time: Literal["prev", "current"],
        scale_name: str,
        expected_length: int,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        if time == "prev":
            prompt = self.prompts["fill_scale"].render(
                scale_name=scale_name,
                profile=self.profile_str,
                report=self.report,
            )
        elif time == "current":
            prompt = self.prompts["fill_scale"].render(
                scale_name=scale_name,
                profile=self.profile_str,
                situation=additional_data.get("situation", ""),
                statement=additional_data.get("statement", ""),
                style=additional_data.get("style", []),
            )
        else:
            raise ValueError("time must be 'prev' or 'current'")
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=ScaleAnswer,
        )

        # Ensure the length of answers is correct
        answers = res.answers
        if len(answers) < expected_length:
            answers.extend(["B"] * (expected_length - len(answers)))
        elif len(answers) > expected_length:
            answers = answers[:expected_length]

        return answers

    def trigger_event(self) -> str:
        """Select triggering event based on age"""
        age = int(self.profile.get("age", 30))

        if age < 18:
            return random.choice(self.teen_events)
        elif age >= 65:
            elderly_events = self.adult_events[self.adult_events["Age"] >= 60]
            if len(elderly_events) > 0:
                return elderly_events.sample(1)["Event"].values[0]

        age_events = self.adult_events[
            (self.adult_events["Age"] >= age - 5)
            & (self.adult_events["Age"] <= age + 5)
        ]
        if len(age_events) > 0:
            return age_events.sample(1)["Event"].values[0]

        return self.events_df.sample(1)["Event"].values[0]

    def generate_complaint_chain(self, event: str) -> List[Dict[str, str]]:
        prompt = self.prompts["complaint_chain_generation"].render(
            profile=self.profile_str,
            event=event,
        )
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=ComplaintChainResponse,
        )

        return [{"stage": node.stage, "content": node.content} for node in res.chain]

    def generate_situation(self, event: str) -> str:
        prompt = self.prompts["situation_generation"].render(
            profile=self.profile_str,
            event=event,
        )
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=SituationResponse,
        )

        return res.situation

    def generate_style(self) -> List[str]:
        prompt = self.prompts["generate_style"].render(
            profile=self.profile_str,
            conv_history=self.prev_conv_str,
        )
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=StyleResponse,
        )

        return res.style

    def generate_statement(self) -> str:
        seeker_utterances = [
            f"{conv['content']}" for conv in self.prev_conv if conv["role"] == "Client"
        ]

        if seeker_utterances:
            k = min(3, len(seeker_utterances))
            return random.choices(seeker_utterances, k=k)
        else:
            return ["Work pressure has been pretty hard recently"]

    def analyze_scale_changes(
        self,
        scale_name: str,
        scale_content: List[str],
        previous: List[str],
        current: List[str],
    ) -> Dict[str, Any]:
        """Analyze changes in a single scale"""
        prompt = self.prompts["analyze_scale_changes"].render(
            scale_name=scale_name,
            scale_content=scale_content,
            previous_answers=previous,
            current_answers=current,
        )

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=ScaleChangesResponse,
        )

        return {
            "changes": [c.model_dump() for c in res.changes],
            "summary": res.summary,
        }

    def summarize_status(self, prev_scales, current_scales) -> str:
        """Summarize the patient's current status"""
        changes = {}
        for scale_name, scale_data in self.scales.items():
            changes[scale_name] = self.analyze_scale_changes(
                scale_name=scale_name,
                scale_content=scale_data,
                previous=prev_scales[scale_name],
                current=current_scales[scale_name],
            )
        prompt = self.prompts["summarize_status"].render(
            bdi_changes=changes["bdi"]["summary"],
            ghq_changes=changes["ghq"]["summary"],
            sass_changes=changes["sass"]["summary"],
        )

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=StatusResponse,
        )

        return res.status

    def generate_character(self):
        """Generate the AnnaAgent character based on the provided data."""
        # 1. Fill in the previous treatment scales
        p_bdi = self.fill_scale("prev", "Beck Depression Scale", 21)
        p_ghq = self.fill_scale("prev", "General Health Questionnaire", 28)
        p_sass = self.fill_scale("prev", "Social Adaptation Self-evaluation Scale", 21)
        prev_scales = {
            "bdi": p_bdi,
            "ghq": p_ghq,
            "sass": p_sass,
        }

        # 2. Generate triggering event
        event = self.trigger_event()

        # 3. Generate complaint cognitive change chain
        complaint_chain = self.generate_complaint_chain(event=event)

        # 4. Initialize current situation, style, statement
        situation = self.generate_situation(event=event)
        style = self.generate_style()
        statement = self.generate_statement()

        # 5. Fill in the current treatment scales
        data = {
            "situation": situation,
            "statement": statement,
            "style": style,
        }
        bdi = self.fill_scale(
            "current", "Beck Depression Scale", 21, additional_data=data
        )
        ghq = self.fill_scale(
            "current", "General Health Questionnaire", 28, additional_data=data
        )
        sass = self.fill_scale(
            "current",
            "Social Adaptation Self-evaluation Scale",
            21,
            additional_data=data,
        )
        current_scales = {
            "bdi": bdi,
            "ghq": ghq,
            "sass": sass,
        }

        # 6. Analyze changes in the scale and summarize status
        status = self.summarize_status(prev_scales, current_scales)

        character = AnnaAgentCharacter(
            profile=self.profile,
            situation=situation,
            statement=statement,
            style=style,
            complaint_chain=complaint_chain,
            status=status,
            report=self.report,
            previous_conversations=self.prev_conv,
        )

        save_json(data=character.model_dump(), output_dir=self.configs.output_dir)
