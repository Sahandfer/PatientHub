from pydantic import Field
from typing import Literal
from pydantic import BaseModel, model_validator

from patienthub.schemas.base import BaseCharacter

TRUST_DELTAS = {
    "increased_significantly": 0.5,
    "increased_slightly": 0.25,
    "unchanged": 0.0,
    "decreased_slightly": -0.25,
    "decreased_significantly": -0.5,
}

REACTIONS = {
    # ── Positive ──
    "understood": "The client felt the therapist accurately grasped what they were saying or feeling. They feel heard and seen.",
    "hopeful": "The client felt more optimistic, encouraged, or reassured. A sense that things could get better.",
    "gained_clarity": "The client gained new awareness: saw a pattern, made a connection, or understood something about themselves they hadn't before. Includes moments of insight, feeling less confused, or seeing things from a new angle.",
    "challenged": "The client felt pushed to think differently or confront something uncomfortable. This can be productive or threatening depending on the client's trust and readiness.",
    # ── Negative ──
    "scared": "The client felt frightened, anxious, or emotionally overwhelmed. This could be due to the therapist touching on something very sensitive, pushing too hard, or moving too fast.",
    "misunderstood": "The client felt the therapist missed the point, got it wrong, or was not on the same page. May trigger correction, frustration, or withdrawal.",
    # ── Neutral ──
    "no_reaction": "The client felt nothing notable in response to the therapist's message. The intervention did not land.",
}

BEHAVIORS = {
    "simple_response": "The client gives brief acknowledgments, 'yes,' 'okay,' 'I see,' or minimal verbal responses that confirm hearing the therapist but don't elaborate.",
    "request": "The client asks for something: information, clarification, advice, or the therapist's opinion. Can be genuine help-seeking or reassurance-seeking.",
    "recounting": "The client narrates events or tells stories — factual, descriptive, external. Reporting what happened rather than exploring meaning.",
    "cognitive_exploration": "The client examines their own thoughts, beliefs, assumptions, or patterns. Goes beyond recounting into active self-analysis.",
    "affective_exploration": "The client explores, expresses, or elaborates on emotions. Naming feelings, connecting them to events, or experiencing them in session.",
    "insight": "The client demonstrates a new understanding — connecting patterns, recognizing causes, an 'aha' moment. A qualitative shift, not just description.",
    "discussing_plans": "The client talks about changes they want to make, actions they intend to try, or new behaviors they have already attempted.",
    "resistance": "The client opposes, deflects, avoids, or blocks the therapeutic process.",
}

RESISTANCE_PATTERNS = {
    # Response Quantity
    "minimal_talk": "Very brief, unelaborated answers. 'I guess,' 'I don't know', 'not really.'",
    # Response Content
    "irrelevant_talk": "Steering the conversation to unrelated topics to avoid the current issue.",
    "superficial": "Staying on surface-level facts and details, avoiding emotional depth.",
    "intellectualizing": "Using analysis, abstract reasoning, or clinical language to avoid experiencing emotions. Talking ABOUT feelings rather than FEELING.",
    # Response Style
    "hostility": "Anger, sarcasm, or sharp criticism directed at the therapist, the process, or the questions being asked.",
    "defensiveness": "Justifying, denying, or explaining away problems when confronted. 'It's not that bad,' 'you don't understand.'",
    "compliance_without_engagement": "Agreeing with everything the therapist says without genuine engagement. 'Yeah, you're right' followed by no change.",
}

CORE_BELIEF_THEMES = {
    "I am unlovable": "Beliefs about being undeserving of love or connection. This theme often involves fears of rejection and abandonment, leading to withdrawal or clinging behaviors in relationships.",
    "I am worthless": "Beliefs about being inadequate, incompetent, or a failure. This theme can manifest as feelings of shame, low self-esteem, and a tendency to avoid challenges or opportunities for growth.",
    "I am helpless": "Beliefs about being powerless, trapped, or unable to cope. This theme may lead to feelings of despair, resignation, and difficulty taking initiative or advocating for oneself.",
}

ATTACHMENT_STYLES = {
    "secure": "the client possesses high self-esteem and view others as reliable. They are comfortable with emotional intimacy and independence, able to communicate their needs, and effectively navigate conflict in relationships.",
    "avoidant": "the client values independence and self-reliance above emotional closeness. Avoidant individuals often suppress difficult emotions, shy away from extreme emotional expression, and may view deep intimacy as a threat to their freedom.",
    "anxious": "the client desires deep intimacy but harbor a profound fear of abandonment. They tend to need constant reassurance and can experience high levels of relationship anxiety, often over-analyzing their partner's behaviors.",
    "disorganized": "the client experiences a confusing pull between craving intimacy and fearing it, making it difficult to trust others and often leading to unpredictable behaviors in relationships. This style is common in individuals who have experienced early trauma or inconsistent caregiving.",
}


class TypicalPresentation(BaseModel):
    mild: str
    moderate: str
    severe: str


class DiseaseOutline(BaseModel):
    key_characteristics: list[str]
    typical_presentation: TypicalPresentation
    important_notes: list[str]
    contraindications: list[str]
    differential_considerations: list[str]
    special_populations: list[str]
    red_flags: list[str]


# ── Seed Schema ───────────────────────────────────────────────────────────


class SampledDemographic(BaseModel):
    gender: Literal["male", "female"]
    age_group: Literal["Child", "Adult", "Elderly"]
    ethnicity: str
    occupation_type: str
    core_belief_theme: Literal["I am unlovable", "I am worthless", "I am helpless"] = (
        Field(
            ...,
            description=(
                "The client's central negative self-belief. "
                "'I am unlovable': beliefs about being undeserving of love or connection. "
                "'I am worthless': beliefs about being inadequate, incompetent, or a failure. "
                "'I am helpless': beliefs about being powerless, trapped, or unable to cope."
            ),
        )
    )
    # attachment_style: Literal["secure", "anxious", "avoidant", "disorganized"] = Field(
    attachment_style: Literal["anxious", "avoidant", "disorganized"] = Field(
        ...,
        description=(
            "How the client relates to others under stress."
            # "secure: can access emotions and seek support appropriately. "
            "anxious: hypervigilant to rejection, reassurance-seeking, difficulty self-soothing. "
            "avoidant: emotionally shut down, self-reliant, uncomfortable with closeness. "
            "disorganized: oscillates between approach and withdrawal, contradictory under stress."
        ),
    )


# ── Profile Schemas ───────────────────────────────────────────────────────


class Demographics(BaseModel):
    name: str = Field(
        ...,
        description="The client's full name, selected from common names.",
    )
    gender: Literal["male", "female"] = Field(
        ..., description="The gender of the client."
    )
    age_group: Literal["Child", "Adult", "Elderly"] = Field(
        ...,
        description="The client's age group. Child: 6-17, Adult: 18-64, Elderly: 65+",
    )
    occupation: str = Field(
        ...,
        description="The client's current job title or employment status.",
    )
    marital_status: Literal[
        "single", "married", "divorced", "widowed", "in a relationship"
    ] = Field(..., description="The marital status of the client.")
    cultural_background: str = Field(
        ...,
        description="The client's nationality, ethnicity, or culturally significant identities.",
    )


class PresentingProblem(BaseModel):
    situation: str = Field(
        ...,
        description="External/referral-perspective summary of what brought the patient to treatment.",
    )
    impact: list[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="Specific observable symptoms and consequences. One item per symptom.",
    )


class PredisposingFactors(BaseModel):
    psychological: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Early experiences and formative relationships that shaped beliefs and coping patterns.",
    )
    social: list[str] = Field(
        ...,
        min_length=1,
        max_length=2,
        description="Environmental, cultural, and interpersonal context that contributed to vulnerability.",
    )


class PerpetuatingFactors(BaseModel):
    internal: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Maintenance cycles that keep the problem going.",
    )
    external: list[str] = Field(
        ...,
        min_length=1,
        max_length=2,
        description="Environmental stressors or interpersonal dynamics that reinforce the problem.",
    )


class ProtectiveFactors(BaseModel):
    internal: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Personal capabilities and motivation for change.",
    )
    external: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Social support and access to practical resources.",
    )


class ProblemFormulation(BaseModel):
    presenting_problem: PresentingProblem
    precipitating_factors: list[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Event(s) or change(s) that triggered the current problem.",
    )
    predisposing_factors: PredisposingFactors
    perpetuating_factors: PerpetuatingFactors
    protective_factors: ProtectiveFactors


class InterpersonalPattern(BaseModel):
    domain: str = Field(
        ...,
        description="The relationship context this pattern applies to.",
        examples=["the therapist", "romantic partner", "peers/friends"],
    )
    wish: str = Field(
        ...,
        description="What the client wants from the other person in this relationship.",
    )
    response_of_other: str = Field(
        ...,
        description="The client's expected or perceived reaction from the other person (subjective).",
    )
    response_of_self: str = Field(
        ...,
        description="How the client reacts emotionally and behaviorally when they perceive that expected response.",
    )


class PsychologicalFormulation(BaseModel):
    intermediate_beliefs: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Self-imposed rules, attitudes, and assumptions derived from core beliefs.",
    )
    automatic_thoughts: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Situation-specific cognitions — what the client actually thinks in distress.",
    )
    triggers: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Situations, topics, or therapist behaviors that activate distress.",
    )
    coping_patterns: list[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Observable behaviors when emotionally threatened.",
    )
    emotional_range: str = Field(
        ...,
        description="Which emotions the client can and cannot access.",
    )
    interpersonal_patterns: list[InterpersonalPattern] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="Relational patterns across key relationship domains.",
    )


# ── Validation Schemas ────────────────────────────────────────────────────


class DemographicCompletionResult(BaseModel):
    passed: bool
    issues: list[str] = Field(default_factory=list)
    rationale: str
    demographics: Demographics | None = None

    @model_validator(mode="after")
    def validate_decision(self):
        if self.passed and self.demographics is None:
            raise ValueError("Passed demographic completion must include demographics.")
        if self.passed and self.issues:
            raise ValueError("Passed demographic completion cannot include issues.")
        if not self.passed and not self.issues:
            raise ValueError("Failed demographic completion must include issues.")
        return self


class ValidationResult(BaseModel):
    passed: bool
    issues: list[str] = Field(default_factory=list)
    rationale: str
    revision_guidance: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_decision(self):
        if self.passed and self.issues:
            raise ValueError("Passed validation cannot include issues.")
        if not self.passed and not self.issues:
            raise ValueError("Failed validation must include issues.")
        return self


# ── Memory Schemas ────────────────────────────────────────────────────────


class MemoryItem(BaseModel):
    field_path: str = Field(
        ...,
        description="Dotted path to the profile field.",
    )
    content: str
    disclosure_level: Literal[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0] = Field(
        ...,
        ge=1.0,
        le=4.0,
        description=(
            "Minimum behavioral trust level at which the client would share this. "
            "1.0=active refusal, 2.0=hesitant, 2.5=session start, "
            "3.0=building trust, 4.0=fully open."
        ),
    )
    activation_tags: list[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="Conversational topics that make this item relevant for retrieval.",
    )
    generates_discomfort: bool = Field(
        ...,
        description=(
            "Whether approaching this topic when trust is insufficient produces "
            "visible discomfort or avoidance (true), or the content simply doesn't "
            "surface (false)."
        ),
    )


class ProfileMemory(BaseModel):
    items: list[MemoryItem] = Field(
        ...,
        description="All memory items with disclosure levels, activation tags, and discomfort flags.",
    )


class PatientActClientCharacter(BaseCharacter):
    demographics: Demographics
    problem_formulation: ProblemFormulation
    psychological_formulation: PsychologicalFormulation


class GeneratedProfile(BaseModel):
    profile: PatientActClientCharacter
    memory: ProfileMemory
    seed: SampledDemographic
    situation: str = Field(
        ..., description="The clinical situation seed used to generate this profile."
    )
    disease_key: str | None = Field(None, description="The disease key used, if any.")
