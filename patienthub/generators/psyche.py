from typing import Literal
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, load_prompts, get_chat_model, save_json


@dataclass
class PsycheGeneratorConfig(APIModelConfig):
    """Configuration for Psyche generator."""

    agent_type: str = "psyche"
    prompt_path: str = "data/prompts/generator/psyche.yaml"
    input_dir: str = "data/resources/psyche_character.json"
    output_dir: str = "data/characters/Psyche MFC.json"


class IdentifyingData(BaseModel):
    age: str = Field(
        ...,
        alias="Age",
        description="Patient's age in years (string for compatibility with existing data).",
        example="40",
    )
    sex: str = Field(
        ...,
        alias="Sex",
        description="Patient's sex.",
        example="Female",
    )
    marital_status: Literal["Single", "Married", "Divorced", "Widowed"] = Field(
        ...,
        alias="Marital status",
        description="Patient's marital status.",
        example="Married",
    )
    occupation: str = Field(
        ...,
        alias="Occupation",
        description="Patient's current occupation or primary role.",
        example="Office worker",
    )


class ChiefComplaint(BaseModel):
    description: str = Field(
        ...,
        alias="Description",
        description="Chief complaint in the patient's own words.",
        example="I feel overwhelmingly sad and have no energy to do anything.",
    )


class PresentIllnessSymptom(BaseModel):
    name: str = Field(
        ...,
        alias="Name",
        description="Primary symptom name.",
        example="Persistent sadness",
    )
    length: int = Field(
        ...,
        alias="Length",
        ge=0,
        le=24,
        description="Duration of the symptom (unit: week).",
        example=24,
    )
    alleviating_factor: str = Field(
        ...,
        alias="Alleviating factor",
        description="Main factor(s) that alleviate the symptom.",
        example="Spending time with family",
    )
    exacerbating_factor: str = Field(
        ...,
        alias="Exacerbating factor",
        description="Main factor(s) that exacerbate the symptom.",
        example="Work stress",
    )
    triggering_factor: str = Field(
        ...,
        alias="Triggering factor",
        description="Triggering factor that led the patient to seek help now.",
        example="Increased workload and stress at work",
    )
    stressor: Literal[
        "work",
        "home",
        "school",
        "legal issue",
        "medical comorbidity",
        "interpersonal difficulty",
        "none",
    ] = Field(
        ...,
        alias="Stressor",
        description="Primary stressor domain",
        example="work",
    )


class PresentIllness(BaseModel):
    symptom: PresentIllnessSymptom = Field(
        ...,
        alias="Symptom",
        description="Structured description of the current symptom.",
    )


class PastPsychiatricHistory(BaseModel):
    presence: str = Field(
        ...,
        alias="Presence",
        description="Whether there is past psychiatric history (e.g., 'Yes' or 'No').",
        example="No",
    )
    description: str | None = Field(
        default=None,
        alias="Description",
        description=(
            "Description of past psychiatric episodes if present; " "otherwise null."
        ),
        example=None,
    )


class PastMedicalHistory(BaseModel):
    presence: str = Field(
        ...,
        alias="Presence",
        description="Whether there is past medical history (e.g., 'Yes' or 'No').",
        example="Yes",
    )
    history: str = Field(
        ...,
        alias="History",
        description="Summary of relevant past medical conditions.",
        example="Hypertension",
    )


class CurrentMedication(BaseModel):
    medication_name: str = Field(
        ...,
        alias="Medication name",
        description="Name of the current medication.",
        example="Amlodipine",
    )
    duration: str = Field(
        ...,
        alias="Duration",
        description="Duration of current medication use.",
        example="52 weeks",
    )
    compliance: str = Field(
        ...,
        alias="Compliance",
        description="Medication adherence/compliance.",
        example="Good",
    )
    effect: str = Field(
        ...,
        alias="Effect",
        description="Clinical effect of the medication.",
        example="Effective",
    )
    side_effect: str = Field(
        ...,
        alias="Side effect",
        description="Presence or absence of notable side effects.",
        example="No",
    )


class FamilyHistory(BaseModel):
    diagnosis: str = Field(
        ...,
        alias="Diagnosis",
        description="Psychiatric family history (diagnoses of relatives).",
        example="Mother diagnosed with major depressive disorder",
    )
    substance_use: str = Field(
        ...,
        alias="Substance use",
        description="Family history of substance use problems.",
        example="Father had a history of alcohol use disorder",
    )


class ChildhoodHistory(BaseModel):
    home_environment: str = Field(
        ...,
        alias="Home environment",
        description="Description of the childhood home environment.",
        example="Supportive but strict",
    )
    members_of_family: str = Field(
        ...,
        alias="Members of family",
        description="Description of family members during childhood.",
        example="Parents and one younger brother",
    )
    social_environment: str = Field(
        ...,
        alias="Social environment",
        description="Childhood social environment and friendships.",
        example="Had a few close friends, mostly kept to herself",
    )


class DevelopmentalSocialHistory(BaseModel):
    childhood_history: ChildhoodHistory = Field(
        ...,
        alias="Childhood history",
        description="Structured childhood history.",
    )
    school_history: str = Field(
        ...,
        alias="School history",
        description="Summary of school performance and issues.",
        example="Low academic performance",
    )
    work_history: str = Field(
        ...,
        alias="Work history",
        description="Summary of work history and occupational functioning.",
        example=(
            "Works as an office worker, good performance, switched jobs twice due "
            "to better opportunities, good relationship with supervisor, mixed "
            "relations with coworkers"
        ),
    )


class Impulsivity(BaseModel):
    suicidal_ideation: Literal["High", "Moderate", "Low"] = Field(
        ...,
        alias="Suicidal ideation",
        description="Level of suicidal ideation (High/Moderate/Low).",
        example="High",
    )
    suicidal_plan: Literal["Presence", "Absence"] = Field(
        ...,
        alias="Suicidal plan",
        description="Presence or absence of suicidal plan.",
        example="Presence",
    )
    suicidal_attempt: Literal["Presence", "Absence"] = Field(
        ...,
        alias="Suicidal attempt",
        description="History of suicidal attempts (Presence/Absence).",
        example="Presence",
    )
    self_mutilating_behavior_risk: Literal["High", "Moderate", "Low"] = Field(
        ...,
        alias="Self-mutilating behavior risk",
        description="Risk level for self-mutilating behavior.",
        example="High",
    )
    homicide_risk: Literal["High", "Moderate", "Low"] = Field(
        ...,
        alias="Homicide risk",
        description="Risk level for homicidal behavior.",
        example="Low",
    )


class MFCProfile(BaseModel):
    identifying_data: IdentifyingData = Field(
        ...,
        alias="Identifying data",
        description="Identifying demographic and occupational data.",
    )
    chief_complaint: ChiefComplaint = Field(
        ...,
        alias="Chief complaint",
        description="Chief complaint section from the MFC-Profile.",
    )
    present_illness: PresentIllness = Field(
        ...,
        alias="Present illness",
        description="Present illness section including the main symptom.",
    )
    past_psychiatric_history: PastPsychiatricHistory = Field(
        ...,
        alias="Past psychiatric history",
        description="Past psychiatric history section.",
    )
    past_medical_history: PastMedicalHistory = Field(
        ...,
        alias="Past medical history",
        description="Past medical history section.",
    )
    current_medication: CurrentMedication = Field(
        ...,
        alias="Current medication",
        description="Current medication section.",
    )
    family_history: FamilyHistory = Field(
        ...,
        alias="Family history",
        description="Family psychiatric and substance use history.",
    )
    developmental_social_history: DevelopmentalSocialHistory = Field(
        ...,
        alias="Developmental/social history",
        description="Developmental and social history section.",
    )
    impulsivity: Impulsivity = Field(
        ...,
        alias="Impulsivity",
        description="Impulsivity and risk section.",
    )


class MFCHistory(BaseModel):
    MFC_History: str = Field(
        ...,
        alias="MFC-History",
        description=(
            "Biography-style dynamic life story in the patient's first-person voice."
        ),
        example="I grew up in a small town with my parents and a younger brother. My parents were supportive but strict, often emphasizing academic success. In school, I struggled to keep up with my classmates and usually ranked in the lower half of the class, which made me feel insecure about my abilities. I had a few close friends but tended to keep to myself, spending most of my free time reading or listening to music.\n\nAs an adult, I started working as an office worker and gradually took on more responsibilities. Although my performance improved and I sometimes received praise from my supervisor, I always felt that I was barely keeping things together. Over the past several months, my workload increased significantly, with frequent deadlines and long hours. Around this time, I began to feel persistently sad and exhausted, losing interest in activities I used to enjoy. I often came home from work and went straight to bed, unable to find the energy to interact with my family.\n\nRecently, these feelings intensified. I started to believe that I was a burden to my family and colleagues, and my sleep and appetite became disturbed. After a particularly stressful week at work, I experienced a crisis point where I seriously considered harming myself. My family noticed the change in my behavior and urged me to seek help, which led me to visit the hospital.",
    )


class MFCBehavior(BaseModel):
    general_appearance_attitude_behavior: str = Field(
        ...,
        alias="General appearance/attitude/behavior",
        description="Detailed description of physical appearance, hygiene, eye contact, motor activity, cooperativeness.",
        example="The patient is a woman in her early 40s, appearing slightly older...",
    )
    mood: str = Field(
        ...,
        alias="Mood",
        description="short label (e.g., 'Depressed', 'Anxious', 'Euphoric') plus, optionally, a direct patient quote that captures the mood.",
        example='Depressed "I feel completely drained, like everything is bleak."',
    )
    affect: str = Field(
        ...,
        alias="Affect",
        description="Ddescribe range, intensity, stability, and appropriateness (e.g., 'Restricted, anxious, slightly tense, not labile, not shallow, not inadequate, not inappropriate').",
    )
    spontaneity: str = Field(
        ...,
        alias="Spontaneity",
        description='indicate whether spontaneity is increased, normal, decreased, or similar (you may use symbols like "(+)" if appropriate).',
    )
    verbal_productivity: Literal["Decreased", "Normal", "Increased"] = Field(
        ...,
        alias="Verbal productivity",
        description="Amount of speech",
        example="Decreased",
    )
    tone_of_voice: str = Field(
        ...,
        alias="Tone of voice",
        description="Tone of voice.",
        example="Low-pitched",
    )
    social_judgement: str = Field(
        ...,
        alias="Social judgement",
        description="Summary of social judgement.",
        example="Normal",
    )
    insight: str = Field(
        ...,
        alias="Insight",
        description="describe how much the patient understands their illness (e.g., full, partial, denial) and optionally include a quote illustrating this.",
    )
    reliability: str = Field(
        ...,
        alias="Reliability",
        description='"Yes" or a short description of whether the patient’s report seems reliable',
        example="Yes",
    )
    perception: str = Field(
        ...,
        alias="Perception",
        description='"Normal" or include hallucinations or other abnormalities if clinically consistent.',
        example="Normal",
    )
    thought_process: str = Field(
        ...,
        alias="Thought process",
        description="Thought process (Normal, Circumstantial, Flight of ideas, etc.).",
        example="Normal",
    )
    thought_content: str = Field(
        ...,
        alias="Thought content",
        description="Describe predominant ideas, worries, delusions, suicidal thoughts, etc., with an illustrative quote if appropriate.",
        example='Preoccupation (+) "I feel like I’m a burden to my company and family."',
    )


class MFC(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    MFC_Profile: MFCProfile = Field(alias="MFC-Profile")
    MFC_History: str = Field(alias="MFC-History")
    MFC_Behavior: MFCBehavior = Field(alias="MFC-Behavior")


class PsycheGenerator(BaseGenerator):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(configs)
        self.data = load_json(configs.generator.input_dir)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.mfc_profile = None
        self.mfc_history = None
        self.mfc_behavior = None

    def generate_mfc_profile(self):

        prompt = self.prompts["MFC_Profile"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
        )
        self.mfc_profile = self.chat_model.generate(
            [{"role": "system", "content": prompt}], responses_format=MFCProfile
        )

    def generate_mfc_history(self):
        profile_json = self.mfc_profile.model_dump_json(by_alias=True)
        prompt = self.prompts["MFC_History"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
            mfc_profile_json=profile_json,
        )
        self.mfc_history = self.chat_model.generate(
            [{"role": "system", "content": prompt}], responses_format=MFCHistory
        )

    def generate_mfc_behavior(self):
        profile_json = self.mfc_profile.model_dump_json(by_alias=True)
        history_json = self.mfc_history.model_dump_json(by_alias=True)
        prompt = self.prompts["MFC_Behavior"].render(
            diagnosis=self.data["diagnosis"],
            age=self.data["age"],
            sex=self.data["sex"],
            mfc_profile_json=profile_json,
            mfc_history_json=history_json,
        )
        self.mfc_behavior = self.chat_model.generate(
            [{"role": "system", "content": prompt}], responses_format=MFCBehavior
        )

    def generate_character(self):
        self.generate_mfc_profile()
        self.generate_mfc_history()
        self.generate_mfc_behavior()

        mfc = MFC(
            MFC_Profile=self.mfc_profile,
            MFC_History=self.mfc_history.MFC_History,
            MFC_Behavior=self.mfc_behavior,
        )

        save_json(
            data=mfc.model_dump(by_alias=True),
            output_dir=self.configs.generator.output_dir,
        )

    def reset(self):
        self.mfc_profile = None
        self.mfc_history = None
        self.mfc_behavior = None
