from dataclasses import dataclass
from typing import Literal, List
from omegaconf import DictConfig
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, load_prompts, get_chat_model, save_json


@dataclass
class StudentClientGeneratorConfig(APIModelConfig):
    """Configuration for Student Client generator."""

    agent_type: str = "student"
    input_dir: str = "data/situations/thu_topics.json"
    output_dir: str = "data/characters/thu/thu_testing.json"
    data_idx: int = 0
    mode: str = "topic"


class Demographics(BaseModel):
    name: str = Field(..., description="Character's name")
    gender: Literal["男", "女"] = Field(..., description="Character's gender")
    age: int = Field(..., description="Character's age")
    major: str = Field(..., description="Character's major")
    year_of_study: str = Field(
        ..., description="Year of study (e.g., freshman, sophomore, junior, senior)"
    )
    marital_status: Literal["单身", "已婚"] = Field(
        ..., description="Character's marital status"
    )


class BigFivePersonality(BaseModel):
    openness: str = Field(
        ...,
        description=(
            "Openness to Experience (BFI): one short sentence or a few keywords describing this trait."
        ),
    )
    conscientiousness: str = Field(
        ...,
        description=(
            "Conscientiousness (BFI): one short sentence or a few keywords describing this trait."
        ),
    )
    extraversion: str = Field(
        ...,
        description=(
            "Extraversion (BFI): one short sentence or a few keywords describing this trait."
        ),
    )
    agreeableness: str = Field(
        ...,
        description=(
            "Agreeableness (BFI): one short sentence or a few keywords describing this trait."
        ),
    )
    neuroticism: str = Field(
        ...,
        description=(
            "Neuroticism (BFI): one short sentence or a few keywords describing this trait."
        ),
    )


class Style(BaseModel):
    conversation_style: str = Field(
        ...,
        description="How the character interacts in conversation (e.g., talkative, reserved)",
    )
    cooperation_level: Literal["高", "中", "低"] = Field(
        ...,
        description=(
            "How willing the character is to cooperate and engage (difficulty). "
        ),
    )


class CoreBeliefs(BaseModel):
    automatic_thoughts: str = Field(
        ...,
        description=("Automatic thoughts related to the issue (2-3 sentences)."),
    )
    values: str = Field(
        ...,
        description=(
            "Values (what matters to the client) related to the issue (2-3 sentences)."
        ),
    )
    attitudes: str = Field(
        ...,
        description=("Attitudes and assumptions related to the issue (2-3 sentences)."),
    )


class CurrentProblem(BaseModel):
    description: str = Field(
        ...,
        description=(
            "Situation description of the client's current problem, including duration (3-5 sentences)."
        ),
    )
    impact: str = Field(
        ...,
        description=(
            "Impact on the client's life, including symptoms and severity (2-5 sentences)."
        ),
    )
    relevant_background: str = Field(
        ...,
        description=(
            "Relevant life events and background, including past experiences, important growth experiences, "
            "and major life events (5-6 sentences)."
        ),
    )
    primary_emotions: List[str] = Field(
        ...,
        description=(
            "2-3 keywords describing the primary emotions triggered by the situation (e.g., anxiety, shame)."
        ),
        min_length=2,
        max_length=3,
    )
    core_beliefs: CoreBeliefs = Field(
        ...,
        description=(
            "Core beliefs: include automatic thoughts, values, and attitudes."
        ),
    )
    core_behaviors: str = Field(
        ...,
        description=(
            "Behaviors in this situation, including triggered behaviors and coping mechanisms (2-3 sentences)."
        ),
    )
    bodily_sensations: str = Field(
        ...,
        description=(
            "Bodily and sensory experiences (e.g., pain, dizziness, pleasant sensations) (2-3 sentences)."
        ),
    )
    interpersonal_status: str = Field(
        ...,
        description=(
            "Current relationships and social interaction with others (family, friends, peers, etc.) (2-3 sentences)."
        ),
    )


class StudentClientProfile(BaseModel):
    title: str = Field(
        ...,
        description=("A short title describing the character and their problem"),
    )
    tag: str = Field(
        ...,
        description=("Problem category tag selected from the allowed tag list"),
    )
    demographics: Demographics = Field(
        ..., description="Demographic information of the character"
    )
    personality: BigFivePersonality = Field(
        ...,
        description=(
            "Personality traits according to the Big Five (BFI). Provide one short sentence or keywords for each factor."
        ),
    )
    style: Style = Field(..., description="Behavioral characteristics of the character")
    current_problem: CurrentProblem = Field(
        ...,
        description="Current problem and related psychological/behavioral context",
    )


class StudentClientGenerator(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs.generator
        self.chat_model = get_chat_model(configs)
        self.data = load_json(self.configs.input_dir)[self.configs.data_idx]
        self.prompts = load_prompts(
            role="generator", agent_type="client", lang=configs.lang
        )

    def generate(self, prompt: str):
        chat_model = self.chat_model.with_structured_output(StudentClientProfile)
        res = chat_model.invoke([SystemMessage(content=prompt)])
        return res

    def create_character(
        self, situation: str = None, label: str = None, topic: str = None
    ):
        prompt = self.prompts[self.configs.mode].render(
            situation=situation, topic=topic, tag=label
        )
        character = self.generate(prompt)
        save_json(character.model_dump(), self.configs.output_dir)

    def reset(self):
        pass


# class Behavior(BaseModel):
#     maladaptive_behaviors: List[str] = Field(
#         default=[],
#         description="Maladaptive behaviors the client wants to stop or change. (e.g., 'What are you doing that you'd like to stop?')",
#         example=[
#             "Avoiding social situations",
#             "Procrastinating on important tasks",
#             "Engaging in self-harm",
#         ],
#     )
#     adaptive_behaviors: List[str] = Field(
#         default=[],
#         description="Adaptive or positive behaviors and coping skills the client engages in. (e.g., 'What are you doing that helps you cope?')",
#         example=[
#             "Exercising regularly",
#             "Practicing mindfulness",
#             "Seeking support from friends",
#         ],
#     )


# class Affect(BaseModel):
#     dominant_emotions: List[str] = Field(
#         ...,
#         description="The most frequently experienced or dominant negative emotions. (e.g., 'What emotions do you experience most often?')",
#         example=["Anxiety", "Sadness", "Anger"],
#     )
#     emotional_triggers: List[str] = Field(
#         default=[],
#         description="Known triggers for strong emotional responses. (e.g., 'What situations or thoughts trigger strong emotions for you?')",
#         example=[
#             "Public speaking",
#             "Conflict with others",
#             "Thinking about past failures",
#         ],
#     )


# class Imagery(BaseModel):
#     self_image: str = Field(
#         ...,
#         description="The client's mental picture or perception of themselves. (e.g., 'How do you see yourself?')",
#         example="I see myself as a failure who can't do anything right.",
#     )
#     recurring_images: List[str] = Field(
#         default=[],
#         description="Any recurring mental pictures, dreams, or unwanted memories. (e.g., 'Do you have any recurring images or memories that bother you?')",
#         example=[
#             "A memory of being bullied in school",
#             "A dream of falling from a great height",
#         ],
#     )


# class Cognition(BaseModel):
#     negative_automatic_thoughts: List[str] = Field(
#         default=[],
#         description="Examples of negative automatic thoughts (NATs). (e.g., 'What negative things do you tell yourself?')",
#         example=[
#             "I'm going to fail",
#             "They all think I'm stupid",
#             "This will never get better",
#         ],
#     )
#     core_beliefs: List[str] = Field(
#         ...,
#         description="Deeper, underlying core beliefs about the self, others, or the world. (e.g., 'What are your core beliefs?')",
#         example=[
#             "I am unlovable",
#             "The world is a dangerous place",
#             "I am not good enough",
#         ],
#     )
#     rules_and_assumptions: List[str] = Field(
#         default=[],
#         description="The client's main 'shoulds,' 'musts,' and 'if-then' rules.",
#         example=["I must always be perfect", "If I ask for help, I am weak"],
#     )


# class Interpersonal(BaseModel):
#     supportive_relationships: List[str] = Field(
#         default=[],
#         description="Significant people in the client's life who are supportive.",
#         example=["My best friend", "My sister", "My mentor"],
#     )
#     conflict_areas: List[str] = Field(
#         default=[],
#         description="Key problem areas or conflicts in relationships.",
#         example=["Frequent arguments with parents", "Feeling isolated from peers"],
#     )


# class Biology(BaseModel):
#     sleep_patterns: str = Field(
#         ...,
#         description="Description of the client's sleep habits and any issues related to sleep.",
#     )
#     exercise_routine: str = Field(
#         ...,
#         description="Description of the client's exercise habits and routines.",
#     )
#     dietary_habits: str = Field(
#         ...,
#         description="Description of the client's eating patterns and dietary habits.",
#     )
#     substance_use: str = Field(
#         ...,
#         description="Information about any substance use, including type, frequency, and quantity.",
#     )


# # Mental state based on Lazarus' BASIC ID framework
# class StudentMentalState(BaseModel):
#     behavior: Behavior = Field(
#         ...,
#         description="Observable actions, acts, habits, and reactions. ",
#     )
#     affect: Affect = Field(
#         ...,
#         description="The full range of emotions, feelings, and moods.",
#     )
#     sensation: str = Field(
#         ...,
#         description="Physical and sensory experiences, such as bodily sensations. This includes specific physical sensations or complaints.",
#     )
#     imagery: Imagery = Field(
#         ...,
#         description="Mental pictures, self-image, recurring dreams, and visualizations of past/future. ",
#     )
#     cognition: Cognition = Field(
#         ..., description="Cognitive patterns and thoughts of the character"
#     )
#     interpersonal: Interpersonal = Field(
#         ...,
#         description="Interpersonal relationships and social interactions of the character. ",
#     )
#     biology: Biology = Field(
#         ...,
#         description="Physical health, nutrition, exercise, sleep, and substance use.",
#     )


# class PersonalHistory(BaseModel):
#     life_history: str = Field(
#         ...,
#         description="A brief overview of the character's life history, including relevant significant events and experiences. (2-3 sentences)",
#     )
#     developmental_history: str = Field(
#         ...,
#         description="A summary of the character's developmental history, including important personal growth experiences and significant life events. Experiences related to the client's problems can be described in more detail. (2-3 sentences)",
#     )
#     family_history: str = Field(
#         ...,
#         description="History of mental illness in immediate family members. (1-2 sentences)",
#     )


# class ConsultationHistory(BaseModel):
#     assessment: str = Field(
#         ...,
#         description="Assessment details including scales like SDS (Depression), SAS (Anxiety), ATS (Suicidal Tendency)",
#     )
#     counseling_history: str = Field(
#         ...,
#         description="History of psychiatric medical history and psychological counseling (e.g., no history of psychiatric medical history, no history of psychological counseling)",
#     )
#     current_consultation_status: str = Field(
#         ..., description="Current consultation status, e.g., nth consultation session"
#     )
#     risk_assessment: str = Field(
#         ..., description="Assessment of the client's risk of suicide and homicide"
#     )
