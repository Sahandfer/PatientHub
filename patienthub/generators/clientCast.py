from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal

from patienthub.base import InferenceAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model, load_json, save_json


@dataclass
class ClientCastGeneratorConfig(APIModelConfig):
    """Configuration for ClientCast generator."""

    agent_type: str = "clientCast"
    input_dir: str = "data/resources/ClientCast/human_data.json"
    symptoms_dir: str = "data/resources/ClientCast/symptoms.json"
    output_dir: str = "data/characters/ClientCast.json"
    data_idx: int = 0


class BasicProfile(BaseModel):
    name: str = Field(
        ...,
        alias="name",
        description="Client's name; use 'Not Specified' if it cannot be identified.",
    )
    gender: Literal["Male", "Female", "Cannot be identified"] = Field(
        ...,
        alias="gender",
        description=("Most probable gender of the client based on the conversation. "),
    )
    age: int = Field(
        ...,
        alias="age",
        description=(
            "Estimated age of the client from the conversation. Give out an approximate age or use -1 if age cannot be reasonably inferred."
        ),
    )
    age_explain: str = Field(
        ...,
        alias="age explain",
        description=(
            "Give out a brief explanation for the estimated age of the client from the conversation or use 'unclear' if age cannot be reasonably inferred. "
        ),
    )
    occupation: str = Field(
        ...,
        alias="occupation",
        description=(
            "Client's occupation inferred from the conversation; use only the occupation or 'Not Specified'/'unclear' when appropriate. "
        ),
    )
    topic: str = Field(
        ...,
        alias="topic",
        description=(
            "Main topic of the conversation chosen from: "
            "'smoking cessation', 'alcohol consumption', 'substance abuse', "
            "'weight management', 'medication adherence', 'recidivism', or 'others', "
            "followed by a short explanation."
        ),
        example="smoking cessation – wants to quit but struggles with cravings.",
    )
    situation: str = Field(
        ...,
        alias="situation",
        description="One-sentence summary of the client's current situation and mental health.",
        example="The client feels overwhelmed by work stress and persistent low mood.",
    )
    emotion: str = Field(
        ...,
        alias="emotion",
        description="One-sentence summary of the client's feelings and emotions.",
        example="The client feels anxious and guilty about disappointing others.",
    )
    reasons: str = Field(
        ...,
        alias="reasons",
        description=(
            "Reasons for the client's visit to the therapist. "
            "The answer should start with 'The client is visiting the therapist because'."
        ),
        example=(
            "The client is visiting the therapist because they feel stuck and unable "
            "to cope with increasing anxiety."
        ),
    )
    problem: str = Field(
        ...,
        alias="problem",
        description=(
            "Main problem the client is currently facing. "
            "Begin with a problem type (e.g., relationship, weight control, "
            "school-related issues) followed by a short explanation."
        ),
        example="relationship – ongoing conflict with partner causing significant distress.",
    )
    emotion_trigger: str = Field(
        ...,
        alias="emotion trigger",
        description=(
            "Therapist behaviors or statements that elicited an emotional reaction "
            "from the client, with direct quotations, or 'No emotional trigger' "
            "if none are present."
        ),
        example=(
            'The therapist asked, "Why didn’t you try harder?", which made the '
            "client tearful."
        ),
    )
    feeling_expression: str = Field(
        ...,
        alias="feeling expression",
        description=(
            "Level of the client's unwillingness to express feelings. "
            "Use one of: 'Low', 'Medium', 'High', or 'Cannot be identified', "
            "followed by a concise one-sentence explanation."
        ),
        example="Medium – the client shares emotions but often minimizes them.",
    )
    emotional_fluctuation: str = Field(
        ...,
        alias="emotional fluctuation",
        description=(
            "Frequency of the client's emotional fluctuations. "
            "Use one of: 'Low', 'Medium', 'High', or 'Cannot be identified', "
            "followed by a concise one-sentence explanation."
        ),
        example="High – the client's mood shifts quickly throughout the conversation.",
    )
    resistance: str = Field(
        ...,
        alias="resistance",
        description=(
            "Level of resistance the client shows toward the therapist. "
            "Use one of: 'Low', 'Medium', 'High', or 'Cannot be identified', "
            "followed by a concise one-sentence explanation."
        ),
        example="Low – the client is open to suggestions and engages collaboratively.",
    )


class BigFiveTraitEstimate(BaseModel):
    score_percent: int = Field(
        ...,
        ge=0,
        le=100,
        description="Estimated level of the trait as an integer percentage from 0 to 100.",
        example=62,
    )
    explanation: str = Field(
        ...,
        description=(
            "A clear, single-sentence explanation grounded in the conversation. "
            "Do not mention the therapist/session/conversation explicitly."
        ),
        example=(
            "The client describes enjoying novel experiences and exploring different "
            "viewpoints, suggesting a moderate-to-high openness."
        ),
    )


class BigFive(BaseModel):
    Openness: BigFiveTraitEstimate = Field(..., description="Openness estimate.")
    Conscientiousness: BigFiveTraitEstimate = Field(
        ..., description="Conscientiousness estimate."
    )
    Extraversion: BigFiveTraitEstimate = Field(
        ..., description="Extraversion estimate."
    )
    Agreeableness: BigFiveTraitEstimate = Field(
        ..., description="Agreeableness estimate."
    )
    Neuroticism: BigFiveTraitEstimate = Field(..., description="Neuroticism estimate.")


class SymptomEstimate(BaseModel):
    identified: bool = Field(
        ...,
        description=(
            "Whether the symptom can be identified from the conversation prior to it."
        ),
    )
    severity_level: Optional[int] = Field(
        ...,
        description="Severity level as an integer (0-3) if identified is true, otherwise null",
    )
    severity_label: Optional[
        Literal[
            "Not at all", "Several days", "More than half the days", "Nearly everyday"
        ]
    ] = Field(
        ...,
        description=(
            "label matching the severity_level if identified is true, otherwise null"
        ),
        example="More than half the days",
    )
    explanation: str = Field(
        ...,
        description=(
            "Brief and clear explanation. Do not reference the therapist/session/conversation explicitly."
        ),
    )


class OQ45Estimate(SymptomEstimate):
    identified: bool = Field(
        ...,
        description=(
            "Whether the symptom can be identified from the conversation prior to it."
        ),
    )
    scale_type: Literal["positive", "negative"] = Field(
        ...,
        description=(
            "Which severity key applies for this OQ-45 item "
            "(positive severity vs negative severity)."
        ),
        example="negative",
    )
    severity_level: Optional[int] = Field(
        ...,
        description="Severity level as an integer (0-3) if identified is true, otherwise null",
    )
    severity_label: Optional[
        Literal["Never", "Rarely", "Sometimes", "Frequently", "Always"]
    ] = Field(
        ...,
        description=(
            "label matching the severity_level if identified is true, otherwise null"
        ),
        example="More than half the days",
    )
    explanation: str = Field(
        ...,
        description=(
            "Brief and clear explanation. Do not reference the therapist/session/conversation explicitly."
        ),
    )


class Symptoms(BaseModel):
    PHQ9: Dict[str, SymptomEstimate] = Field(
        ...,
        description="PHQ-9 item estimates keyed by item number as string.",
    )
    GAD7: Dict[str, SymptomEstimate] = Field(
        ...,
        description="GAD-7 item estimates keyed by item number as string.",
    )
    OQ45: Dict[str, OQ45Estimate] = Field(
        ...,
        description="OQ-45 item estimates keyed by item number as string.",
    )


class ClientCastCharacter(BaseModel):
    basic_profile: BasicProfile = Field(..., description="Client's basic profile.")
    big_five: BigFive = Field(..., description="Client's Big Five personality traits.")
    symptoms: Symptoms = Field(..., description="Client's symptom estimates.")


class ClientCastGenerator(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(self.configs)
        self.conv_history = self.load_data()
        self.symptoms = load_json(self.configs.symptoms_dir)
        self.prompts = load_prompts(
            role="generator", agent_type="clientCast", lang=configs.lang
        )

    def load_data(self):
        data = load_json(self.configs.input_dir)[self.configs.data_idx]
        return "\n".join(
            [f"{msg['role']}: {msg['content']}\n" for msg in data.get("messages", [])]
        ).strip()

    def generate_basic_profile(self) -> BasicProfile:
        prompt = self.prompts["basic_profile_prompt"].render(
            conversation=self.conv_history
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=BasicProfile
        )
        return res

    def generate_big_five(self) -> BigFive:
        prompt = self.prompts["big_five_prompt"].render(conversation=self.conv_history)
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}], response_format=BigFive
        )
        return res

    def generate_symptoms(self) -> Symptoms:
        full_res = {}
        for disorder, symptoms in self.symptoms.items():
            for i, symptom in enumerate(symptoms):
                prompt = self.prompts["symptoms_prompt"].render(
                    conversation=self.conv_history, symptom=symptom
                )
                if disorder == "OQ-45":
                    res = self.chat_model.generate(
                        [{"role": "system", "content": prompt}],
                        response_format=OQ45Estimate,
                    )
                else:
                    res = self.chat_model.generate(
                        [{"role": "system", "content": prompt}],
                        response_format=SymptomEstimate,
                    )
                full_res[disorder.replace("-", "")] = {f"{i+1}": res}
                # For the sake of API cost, we only do this for one symptom from each disorder
                break

        return Symptoms(
            PHQ9=full_res["PHQ9"], GAD7=full_res["GAD7"], OQ45=full_res["OQ45"]
        )

    def generate_character(self) -> Dict[str, Any]:
        basic_profile = self.generate_basic_profile()
        big_five = self.generate_big_five()
        symptoms = self.generate_symptoms()

        character = ClientCastCharacter(
            basic_profile=basic_profile,
            big_five=big_five,
            symptoms=symptoms,
        )

        save_json(
            data=character.model_dump(),
            output_dir=self.configs.output_dir,
        )
