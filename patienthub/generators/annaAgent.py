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
from typing import Any, Optional, Literal

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json
from patienthub.resources import GHQ, SASS, BDI
from patienthub.schemas.annaAgent import AnnaAgentCharacter, ComplaintNode


@dataclass
class AnnaAgentGeneratorConfig(APIModelConfig):
    """Configuration for AnnaAgent generator."""

    agent_name: str = "annaAgent"
    prompt_path: str = "data/prompts/generator/annaAgent.yaml"
    events_path: str = "data/resources/annaAgent_events.json"


class ComplaintChainResponse(BaseModel):
    chain: list[ComplaintNode] = Field(
        description="Cognitive change chain of the chief complaint, containing 3-7 stages",
        min_length=3,
        max_length=7,
    )


class StyleResponse(BaseModel):
    style: list[str] = Field(
        description="Patient's speaking style characteristics, 1-5 items",
        min_length=1,
        max_length=5,
    )


class ChangeItem(BaseModel):
    item: str = Field(description="Content or number of the item")
    change: Literal["Improved", "Worsened", "No Change"] = Field(
        description="Type of change"
    )
    explanation: str = Field(description="Explanation of the change")


class ScaleChangesResponse(BaseModel):
    changes: list[ChangeItem] = Field(
        description="Analysis of changes for each item in the scale"
    )
    summary: str = Field(description="Summary of overall change trends")


class AnnaAgentGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

        self.events = load_json(self.configs.events_path)[self.configs.lang]
        self.scales = {
            "ghq": GHQ.questions,
            "sass": SASS.questions,
            "bdi": BDI.questions,
        }

    def set_data(self, data: list[dict[str, Any]]):
        """Set the data for the generator."""
        self.data = data
        self.profile = self.data.get("profile", {})
        self.profile_str = self.prompts["profile"].render(profile=self.profile)
        self.report = self.data.get("report", "")
        self.prev_conv = self.data.get("previous_conversations", [])
        self.prev_conv_str = "\n".join(
            [f"{conv['role']}: {conv['content']}" for conv in self.prev_conv]
        )

    def fill_scale(
        self,
        time: Literal["prev", "current"],
        scale_name: str,
        expected_length: int,
        additional_data: Optional[dict[str, Any]] = None,
    ) -> list[str]:
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
            response_format=list[Literal["A", "B", "C", "D"]],
        )

        # Ensure the length of answers is correct
        answers = res
        if len(answers) < expected_length:
            answers.extend(["B"] * (expected_length - len(answers)))
        elif len(answers) > expected_length:
            answers = answers[:expected_length]

        return answers

    def trigger_event(self) -> str:
        """Select an age-matched triggering event (original AnnaAgent logic).

        Teens (<18) draw from the teen list; seniors (>=65) from events aged 60+;
        everyone else from events within +/-5 years of their age (falling back to
        all adult events if none match).
        """
        age = int(self.profile.get("age", 30))
        if age < 18:
            return random.choice(self.events["teen"])
        adult = self.events["adult"]
        if age >= 65:
            pool = [e for e in adult if e["age"] >= 60]
        else:
            pool = [e for e in adult if age - 5 <= e["age"] <= age + 5]
        return random.choice(pool or adult)["event"]

    def generate_complaint_chain(self, event: str) -> list[dict[str, str]]:
        prompt = self.prompts["complaint_chain_generation"].render(
            profile=self.profile_str,
            event=event,
        )
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=ComplaintChainResponse,
        )

        return res.chain

    def generate_situation(self, event: str) -> str:
        prompt = self.prompts["situation_generation"].render(
            profile=self.profile_str,
            event=event,
        )
        return self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=str,
        )

    def generate_style(self) -> list[str]:
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
        scale_content: list[str],
        previous: list[str],
        current: list[str],
    ) -> dict[str, Any]:
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

        return self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=str,
        )

    def generate_character(self, data: dict[str, Any]) -> AnnaAgentCharacter:
        """Generate the AnnaAgent character based on the provided data."""

        # 0. Load up the data required for generation (profile, report, previous conversations)
        self.set_data(data)

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

        return AnnaAgentCharacter(
            profile=self.profile,
            situation=situation,
            statement=statement,
            style=style,
            complaint_chain=complaint_chain,
            status=status,
            report=self.report,
            previous_conversations=self.prev_conv,
        )
