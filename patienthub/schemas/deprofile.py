# coding=utf-8
# Licensed under the MIT License;

import math
from typing import Any, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

from patienthub.schemas.base import BaseCharacter
from patienthub.utils import load_json, resolve_path

Gender = Literal["F", "M", "Unknown"]
MaritalStatus = Literal["single", "married", "divorced", "widowed", "Unknown"]
WorkStatus = Literal["student", "employed", "unemployed", "retired", "Unknown"]
AgeBand = Literal["0-17", "18-25", "26-35", "36-50", "50+", "Unknown"]


CONSTANTS_PATH = "data/resources/Deprofile/constants.json"
CONSTANTS = load_json(resolve_path(CONSTANTS_PATH))
SECTIONS = ["symptom_descriptions", "days"]
SOCIAL_SYMPTOM_TO_CLINICAL: dict[str, str] = {
    "Catatonic_behavior": "任务-躯体症状-运动性迟滞",
    "Decreased_energy_tiredness_fatigue": "任务-精神状态-疲倦",
    "Depressed_Mood": "任务-情绪-情绪低落",
    "Hyperactivity_agitation": "任务-躯体症状-运动性激越",
    "Inattention": "任务-精神状态-注意力不集中",
    "Indecisiveness": "任务-精神状态-选择困难",
    "Suicidal_ideas": "任务-自杀-存在自杀倾向",
    "Worthlessness_and_guilty": "任务-自杀-自我价值感低",
    "diminished_emotional_expression": "任务-兴趣-情感淡漠",
    "drastical_shift_in_mood_and_energy": "任务-筛查-躁狂",
    "fear_about_social_situations": "任务-社会功能-避免与人接触",
    "fear_of_gaining_weight": "任务-食欲-显著体重变化",
    "loss_of_interest_or_motivation": "任务-兴趣-兴趣丧失",
    "pessimism": "任务-自杀-有无望感",
    "poor_memory": "任务-精神状态-记忆力下降",
    "sleep_disturbance": "任务-睡眠-存在睡眠问题",
    "somatic_symptoms_sensory": "任务-躯体症状-躯体不适",
    "weight_and_appetite_change": "任务-食欲-食欲存在问题",
}


def get_constant_dict(section: str, lang: str = "zh") -> dict[str, Any]:
    if section not in SECTIONS:
        raise ValueError(f"invalid section {section}; expected one of {SECTIONS}")
    data = CONSTANTS.get(section, {})
    return data.get(lang) or data.get("zh", {})


def days_to_relative(days_ago: int | None, lang: str = "zh") -> str:
    """Render a relative-day count using the localized ``days`` templates."""
    if days_ago is None:
        return ""
    templates = get_constant_dict("days", lang)
    if days_ago <= 0:
        return templates.get("today", "")
    if days_ago == 1:
        return templates.get("yesterday", "")
    if days_ago < 7:
        return templates.get("days_ago", "{days}").format(days=days_ago)
    if days_ago < 30:
        return templates.get("weeks_ago", "{weeks}").format(weeks=days_ago // 7)
    if days_ago < 365:
        return templates.get("months_ago", "{months}").format(months=days_ago // 30)
    return templates.get("years_ago", "{years}").format(years=days_ago // 365)


class BigFive(BaseModel):
    Openness: float
    Conscientiousness: float
    Extraversion: float
    Agreeableness: float
    Neuroticism: float


class CandidateMatch(BaseModel):
    basic_id: str
    similarity: float
    symp_similarity: float


class ClinicalProfile(BaseModel):
    cr_id: str
    d4_id: str
    age: int = Field(ge=0)
    gender: Gender
    marital_status: MaritalStatus
    work_status: WorkStatus
    big_five: BigFive
    positive_symptoms: list[str]
    negative_symptoms: list[str]
    summation: str | None = None
    depression_risk: int = Field(ge=0, le=3)
    suicide_risk: int = Field(
        ge=0,
        le=3,
        validation_alias=AliasChoices("suicide_risk", "suiside_risk"),
    )
    candidate_id: list[CandidateMatch] = Field(default_factory=list)

    @field_validator("summation", mode="before")
    @classmethod
    def normalize_nan_summary(cls, value: Any) -> Any:
        if isinstance(value, float) and math.isnan(value):
            return None
        return value


class SocialProfile(BaseModel):
    gender: Gender
    age: AgeBand
    marital_status: MaritalStatus
    work_status: WorkStatus
    big_five: BigFive
    symptoms: list[str] = Field(min_length=1)
    life_events: bool | None = None
    prompt_count: int | None = Field(default=None, ge=0)

    @field_validator("symptoms")
    @classmethod
    def require_mappable_symptoms(cls, value: list[str]) -> list[str]:
        unsupported = [
            symptom for symptom in value if symptom not in SOCIAL_SYMPTOM_TO_CLINICAL
        ]
        if unsupported:
            raise ValueError(
                "unsupported social symptom labels: "
                f"{sorted(set(unsupported))}; expected labels from "
                f"{sorted(SOCIAL_SYMPTOM_TO_CLINICAL)}"
            )
        return value


class SocialProfileCatalog(RootModel[dict[str, SocialProfile]]):
    """The social_user_profiles.json resource keyed by social user ID."""

    root: dict[str, SocialProfile] = Field(min_length=1)

    @field_validator("root")
    @classmethod
    def require_non_empty_user_ids(
        cls, value: dict[str, SocialProfile]
    ) -> dict[str, SocialProfile]:
        empty_ids = [user_id for user_id in value if not str(user_id).strip()]
        if empty_ids:
            raise ValueError("social profile user IDs must be non-empty strings")
        return value


class AssessmentMessage(BaseModel):
    role: Literal["doctor", "user"]
    content: str = Field(min_length=1)


class CounselingMessage(BaseModel):
    role: Literal["consultant", "patient"]
    content: str = Field(min_length=1)


class SymptomTimelineItem(BaseModel):
    timestamp: int
    symptom: str
    tweet: str


class SymptomTimeline(BaseModel):
    user_id: str
    symptoms: list[str]
    timeline: list[SymptomTimelineItem] = Field(min_length=1)


class LifeEventTimelineItem(BaseModel):
    timestamp: int
    life_event: str
    tweet: str


class LifeEventTimeline(BaseModel):
    user_id: str
    timeline: list[LifeEventTimelineItem] = Field(min_length=1)


class MatchStageCounts(BaseModel):
    total: int = 0
    timeline_eligible: int = 0
    demographic_compatible: int = 0
    symptom_compatible: int = 0
    personality_compatible: int = 0


class MatchMetadata(BaseModel):
    mode: Literal["index", "rematch"]
    selected_social_user_id: str
    candidate_rank: int = Field(ge=0)
    personality_similarity: float
    symptom_similarity: float
    combined_score: float
    personality_threshold: float
    symptom_threshold: float
    stage_counts: MatchStageCounts | None = None


class TimelineMemory(BaseModel):
    symptom: dict[str, Any]
    life_event: dict[str, Any]


class CoCExtraction(BaseModel):
    is_meaningful: bool = Field(
        description=(
            "Whether the post describes a personal, timeline-relevant "
            "symptom experience or life event for the user."
        )
    )
    event_triple: str | None = Field(
        default=None,
        description=(
            "One concise grounded triple in the form "
            "'subject | experience/action | object/impact'."
        ),
    )
    summary: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "summary", "event_summary_cn", "symptom_summary_cn"
        ),
        description="A short summary using only facts present in the post.",
    )

    @model_validator(mode="after")
    def require_grounded_fields_for_meaningful(self) -> "CoCExtraction":
        if self.is_meaningful and (
            not self.event_triple
            or not self.event_triple.strip()
            or not self.summary
            or not self.summary.strip()
        ):
            raise ValueError(
                "meaningful CoC extractions require event_triple and summary"
            )
        return self


class Provenance(BaseModel):
    generator_version: str
    language: str
    source_paths: dict[str, str]
    completeness: dict[str, bool]


class DeprofileCharacter(BaseCharacter):
    """A patient profile assembled from clinical and social evidence."""

    profile_id: str
    clinical_profile: ClinicalProfile
    assessment_dialogue: list[AssessmentMessage] = Field(min_length=1)
    counseling_dialogue: list[CounselingMessage] = Field(min_length=1)
    social_user_id: str
    symptom_timeline: SymptomTimeline
    life_event_timeline: LifeEventTimeline
    timeline_memory: TimelineMemory | None = None
    match_metadata: MatchMetadata
    provenance: Provenance


class DeprofileSeed(BaseModel):
    profile_id: str
    candidate_rank: int = 0
