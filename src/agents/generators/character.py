from agents import BaseAgent
from typing import Literal, List
from pydantic import BaseModel, Field
from utils import load_prompts
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage


class StudentDemographics(BaseModel):
    name: str = Field(..., description="Character's name")
    age: int = Field(..., description="Character's age")
    gender: Literal["male", "female"] = Field(..., description="Character's gender")
    major: str = Field(..., description="Character's major and year of study")
    marital_status: Literal["single", "married"] = Field(
        ..., description="Character's marital status"
    )


class StudentPersonality(BaseModel):
    extraversion: int = Field(
        ..., description="Extraversion score on a scale from 1 to 10"
    )
    agreeableness: int = Field(
        ..., description="Agreeableness score on a scale from 1 to 10"
    )
    conscientiousness: int = Field(
        ..., description="Conscientiousness score on a scale from 1 to 10"
    )
    neuroticism: int = Field(
        ..., description="Neuroticism score on a scale from 1 to 10"
    )
    openness: int = Field(..., description="Openness score on a scale from 1 to 10")
    summary: str = Field(
        ..., description="A brief summary of the character's personality traits"
    )


class StudentCurrentIssue(BaseModel):
    description: str = Field(
        ...,
        description="A short description of the current issue or problem (< 100 words)",
    )
    symptoms: str = Field(
        ..., description="Symptoms or signs that indicate the presence of the issue"
    )

    duration: str = Field(
        ..., description="Duration for which the character has been facing this issue"
    )
    severity: Literal["mild", "moderate", "severe"] = Field(
        ..., description="Severity of the issue"
    )
    impact: str = Field(..., description="Impact of the issue on the character's life")
    coping_strategies: list[str] = Field(
        ...,
        description="Coping strategies the character has tried or is using to deal with the issue. Can be None if no strategies have been tried.",
    )


# Mental model based on BASK-R framework (Behavior, Affect, Sensation, Knowledge, and Relationships)
# class StudentMentalState(BaseModel):
#     behavior: str = Field(
#         ...,
#         description="Observable behaviors related to the issue. This includes indications of maladaptive behaviors, habits, or behavioral patterns.",
#     )
#     affect: str = Field(
#         ...,
#         description="Emotional states and feelings. This includes indications of maladaptive emotional distress. For example, dominant emotions, emotional experiences, intensity and scope of emotional expression, and emotional regulation abilities.",
#     )
#     sensation: str = Field(
#         ...,
#         description="Physical sensations and symptoms. This includes indications of maladaptive bodily sensations and experiences, or psychosomatic problems.",
#     )
#     knowledge: str = Field(
#         ...,
#         description="Cognitive patterns and beliefs. This includes indications of maladaptive thoughts, beliefs, or core beliefs, including those concerning oneself, others, and things.",
#     )
#     relationships: str = Field(
#         ...,
#         description="Social interactions and support systems. This includes indications of maladaptive interpersonal distress. Interpersonal skills and support.",
#     )


class Cognition(BaseModel):
    negative_automatic_thoughts: List[str] = Field(
        default=[],
        description="Examples of negative automatic thoughts (NATs). (e.g., 'What negative things do you tell yourself?')",
        example=[
            "I'm going to fail",
            "They all think I'm stupid",
            "This will never get better",
        ],
    )
    core_beliefs: List[str] = Field(
        ...,
        description="Deeper, underlying core beliefs about the self, others, or the world. (e.g., 'What are your core beliefs?')",
        example=[
            "I am unlovable",
            "The world is a dangerous place",
            "I am not good enough",
        ],
    )
    rules_and_assumptions: List[str] = Field(
        default=[],
        description="The client's main 'shoulds,' 'musts,' and 'if-then' rules.",
        example=["I must always be perfect", "If I ask for help, I am weak"],
    )


# Mental state based on Lazarus' BASIC ID framework
class StudentMentalState(BaseModel):
    behavior: str = Field(
        ...,
        description="Observable actions, acts, habits, and reactions. What the person does or doesn't do. This includes Maladaptive behaviors the client wants to stop or change. (e.g., 'What are you doing that you'd like to stop?') and adaptive or positive behaviors and coping skills the client engages in.",
    )
    affect: str = Field(
        ...,
        description="The full range of emotions, feelings, and moods. This includes the most frequently experienced or dominant negative emotions and known triggers for strong emotional responses..",
    )
    sensation: str = Field(
        ...,
        description="Physical and sensory experiences, such as bodily sensations. This includes specific physical sensations or complaints.",
    )
    imagery: str = Field(
        ...,
        description="Mental pictures, self-image, recurring dreams, and visualizations of past/future. This includes the client's 'self-image'; how they visualize or perceive themselves and any recurring mental pictures, dreams, or unwanted memories.",
    )
    cognition: Cognition = Field(
        ..., description="Cognitive patterns and thoughts of the character"
    )
    interpersonal: str = Field(
        ...,
        description="Interpersonal relationships and social interactions of the character. This includes significant people in the client's life who are supportive and key problem areas or conflicts in relationships.",
    )
    biology: str = Field(
        ...,
        description="Physical health, nutrition, exercise, sleep, and substance use. This includes a summary of the client's sleeping habits, exercise routines, dietary patterns, and any substance use.",
    )


class StudentClientProfile(BaseModel):
    demographics: StudentDemographics = Field(
        ..., description="Demographic information of the character"
    )
    personality: StudentPersonality = Field(
        ..., description="Personality traits and attributes of the character"
    )
    mental_state: StudentMentalState = Field(
        ..., description="Current mental state based on BASK-R framework"
    )
    current_issue: StudentCurrentIssue = Field(
        ..., description="Current issue the character is facing"
    )


class StudentClientGenerator(BaseAgent):
    def __init__(self, model_client: BaseChatModel, lang: str):
        self.role = "generator"
        self.agent_type = "client"
        self.model_client = model_client
        self.lang = lang
        self.prompts = load_prompts(
            role=self.role, agent_type=self.agent_type, lang=lang
        )

    def generate(self, prompt: str):
        model_client = self.model_client.with_structured_output(StudentClientProfile)
        res = model_client.invoke([SystemMessage(content=prompt)])
        return res

    def save_characters(self, file_path="characters.json"):
        pass

    def create_character(
        self, situation: str = None, topic: str = None
    ) -> StudentClientProfile:
        prompt_type = "basic"
        if topic is not None:
            prompt_type = "with_topic"
        elif situation is not None:
            prompt_type = "with_situation"
        # lang = "English" if self.lang == "en" else "Chinese (中文)"
        lang = "Chinese (中文)"
        prompt = self.prompts[prompt_type].render(
            situation=situation, topic=topic, lang=lang
        )
        character = self.generate(prompt)
        print(character.model_dump_json())

    def reset(self):
        pass
