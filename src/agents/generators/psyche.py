import json
from typing import Any, Dict

from omegaconf import DictConfig
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field

from src.utils import load_prompts, get_model_client


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
    marital_status: str = Field(
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
    length: str = Field(
        ...,
        alias="Length",
        description="Duration of the symptom (e.g., '24 weeks').",
        example="24 weeks",
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
    stressor: str = Field(
        ...,
        alias="Stressor",
        description="Primary stressor domain (e.g., work, home, school).",
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
            "Description of past psychiatric episodes if present; "
            "otherwise null."
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
    suicidal_ideation: str = Field(
        ...,
        alias="Suicidal ideation",
        description="Level of suicidal ideation (High/Moderate/Low).",
        example="High",
    )
    suicidal_plan: str = Field(
        ...,
        alias="Suicidal plan",
        description="Presence or absence of suicidal plan.",
        example="Presence",
    )
    suicidal_attempt: str = Field(
        ...,
        alias="Suicidal attempt",
        description="History of suicidal attempts (Presence/Absence).",
        example="Presence",
    )
    self_mutilating_behavior_risk: str = Field(
        ...,
        alias="Self-mutilating behavior risk",
        description="Risk level for self-mutilating behavior.",
        example="High",
    )
    homicide_risk: str = Field(
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
    mfc_history: str = Field(
        ...,
        alias="MFC-History",
        description=(
            "Biography-style dynamic life story in the patient's first-person voice."
        ),
        example="I grew up in a small town with my parents...",
    )


class MFCBehavior(BaseModel):
    general_appearance_attitude_behavior: str = Field(
        ...,
        alias="General appearance/attitude/behavior",
        description="Detailed description of appearance, attitude, and behavior.",
        example="The patient is a woman in her early 40s, appearing slightly older...",
    )
    mood: str = Field(
        ...,
        alias="Mood",
        description="Mood label plus optional quote.",
        example='Depressed "I feel completely drained, like everything is bleak."',
    )
    affect: str = Field(
        ...,
        alias="Affect",
        description="Description of affect: range, intensity, stability, appropriateness.",
    )
    spontaneity: str = Field(
        ...,
        alias="Spontaneity",
        description="Level of spontaneity (e.g., Decreased/Normal/Increased or symbols like (+)).",
        example="(+)",
    )
    verbal_productivity: str = Field(
        ...,
        alias="Verbal productivity",
        description="Amount of speech (e.g., Decreased/Normal/Increased).",
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
        description="Insight into illness, optionally with a quote.",
    )
    reliability: str = Field(
        ...,
        alias="Reliability",
        description="Reliability of the patient's report.",
        example="Yes",
    )
    perception: str = Field(
        ...,
        alias="Perception",
        description="Perception (e.g., Normal or hallucinations, etc.).",
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
        description=(
            "Predominant thought content (worries, delusions, suicidality), "
            "optionally with a quote."
        ),
        example='Preoccupation (+) "I feel like I’m a burden to my company and family."',
    )


class PsycheGenerator:
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.model_client = get_model_client(configs)
        self.prompts = load_prompts(
            role="generator", agent_type="psyche", lang=configs.lang
        )

    def generate_mfc_profile(
        self, diagnosis: str, age: int, sex: str
    ) -> MFCProfile:
        prompt = self.prompts["MFC_Profile_generate_prompt"].render(
            diagnosis=diagnosis,
            age=age,
            sex=sex,
        )
        model_client = self.model_client.with_structured_output(MFCProfile)
        res = model_client.invoke([SystemMessage(content=prompt)])
        return res

    def generate_mfc_history(
        self, diagnosis: str, age: int, sex: str, mfc_profile: MFCProfile
    ) -> MFCHistory:
        profile_json = json.dumps(
            mfc_profile.model_dump(by_alias=True, mode="json"),
            ensure_ascii=False,
            indent=2,
        )
        prompt = self.prompts["MFC_History_generate_prompt"].render(
            diagnosis=diagnosis,
            age=age,
            sex=sex,
            mfc_profile_json=profile_json,
        )
        model_client = self.model_client.with_structured_output(MFCHistory)
        res = model_client.invoke([SystemMessage(content=prompt)])
        return res

    def generate_mfc_behavior(
        self,
        diagnosis: str,
        age: int,
        sex: str,
        mfc_profile: MFCProfile,
        mfc_history: MFCHistory,
    ) -> MFCBehavior:
        profile_json = json.dumps(
            mfc_profile.model_dump(by_alias=True, mode="json"),
            ensure_ascii=False,
            indent=2,
        )
        history_json = json.dumps(
            mfc_history.model_dump(by_alias=True, mode="json"),
            ensure_ascii=False,
            indent=2,
        )
        prompt = self.prompts["MFC_Behavior_generate_prompt"].render(
            diagnosis=diagnosis,
            age=age,
            sex=sex,
            mfc_profile_json=profile_json,
            mfc_history_json=history_json,
        )
        model_client = self.model_client.with_structured_output(MFCBehavior)
        res = model_client.invoke([SystemMessage(content=prompt)])
        return res

    def generate_case(self, diagnosis: str, age: int, sex: str) -> Dict[str, Any]:
        mfc_profile = self.generate_mfc_profile(diagnosis=diagnosis, age=age, sex=sex)
        mfc_history = self.generate_mfc_history(
            diagnosis=diagnosis,
            age=age,
            sex=sex,
            mfc_profile=mfc_profile,
        )
        mfc_behavior = self.generate_mfc_behavior(
            diagnosis=diagnosis,
            age=age,
            sex=sex,
            mfc_profile=mfc_profile,
            mfc_history=mfc_history,
        )

        case = {
            "Diagnosis": diagnosis,
            "Age": age,
            "Sex": sex,
            "MFC-Profile": mfc_profile.model_dump(by_alias=True, mode="json"),
            "MFC-History": mfc_history.mfc_history,
            "MFC-Behavior": mfc_behavior.model_dump(by_alias=True, mode="json"),
        }
        return case
