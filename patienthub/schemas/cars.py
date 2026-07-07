from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class CarsSource(BaseModel):
    paper: str = Field(...)
    location: str = Field(...)
    status: str = Field(...)


class CarsPaperTrace(BaseModel):
    direct_paper_fields: list[str] = Field(default_factory=list)
    generated_fields: list[str] = Field(default_factory=list)


class CarsDemographics(BaseModel):
    age: str | None = None
    occupation: str | None = None
    gender: str | None = None


class MainCognitiveConceptualizationDiagram(BaseModel):
    relevant_history: str = ""
    core_beliefs: list[str] = Field(default_factory=list)
    intermediate_beliefs: list[str] = Field(default_factory=list)
    coping_strategies: list[str] = Field(default_factory=list)


class SessionSpecificCognitiveConceptualizationDiagram(BaseModel):
    theme: str = ""
    structured_cbt_strategy: str = ""
    situation: str = Field(...)
    automatic_thoughts: list[str] = Field(default_factory=list)
    intermediate_beliefs: list[str] = Field(default_factory=list)
    expected_reactions: list[str] = Field(default_factory=list)
    resistance_triggers: list[str] = Field(default_factory=list)


class CarsPreferences(BaseModel):
    positive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)


class CarsClientCharacteristics(BaseModel):
    possible_responses_under_different_emotions: list[str] = Field(
        default_factory=list
    )
    other_client_characteristics: list[str] = Field(default_factory=list)


class EmotionUtteranceExample(BaseModel):
    emotion: str = Field(...)
    utterance: str = Field(...)
    nonverbal_behavior: str = ""


class ExampleInteraction(BaseModel):
    counselor: str = ""
    client: str = ""


class ExampleStateUpdate(BaseModel):
    emotion: str = ""
    intention: str = ""
    nonverbal_cue: str = ""


class CarsPersonaGenerationOutput(BaseModel):
    """Paper Appendix A.2 output for CARS persona generation."""

    name: str = Field(...)
    age: str = Field(...)
    gender: str = Field(...)
    occupation: str = Field(...)
    family_background: str = Field(...)
    interpersonal_relationships: str = Field(...)
    physical_condition: str = Field(...)
    lifestyle: str = Field(...)
    chief_complaint: str = Field(...)


class CarsGeneratorAutomaticThought(BaseModel):
    situation: str = Field(...)
    cognition: str = Field(...)
    reaction: str = Field(...)


class CarsGeneratorIntermediateBelief(BaseModel):
    attitude: str = Field(...)
    assumption: str = Field(...)
    rule: str = Field(...)


class CarsGeneratorBelief(BaseModel):
    theme: str = Field(
        description=(
            "CBT theme for the generated session belief, such as session "
            "structuring, problem solving and homework, goal setting, cognitive "
            "change, cognitive identification, or therapeutic alliance."
        )
    )
    automatic_thought: CarsGeneratorAutomaticThought = Field(...)
    intermediate_belief: CarsGeneratorIntermediateBelief = Field(...)


class CarsGeneratorEmotionResponse(BaseModel):
    dialogue_style: str = Field(...)
    nonverbal_behavior: str = Field(...)


class CarsGeneratorPreferencePair(BaseModel):
    first: str = Field(...)
    second: str = Field(...)


class CarsGeneratorPolarPreferences(BaseModel):
    positive: CarsGeneratorPreferencePair = Field(...)
    negative: CarsGeneratorPreferencePair = Field(...)


class CarsGeneratorClientCharacteristicsAndPreferences(BaseModel):
    possible_responses_under_different_emotions: CarsGeneratorEmotionResponse = Field(
        ...
    )
    preferred_counselor_style: CarsGeneratorPolarPreferences = Field(...)
    other_client_characteristics: CarsGeneratorPolarPreferences = Field(...)


class CarsCognitivePatternGenerationOutput(BaseModel):
    """Paper Appendix A.2 JSON output for CARS cognitive pattern generation."""

    background: str = Field(...)
    beliefs: list[CarsGeneratorBelief] = Field(default_factory=list)
    client_characteristics_and_preferences: (
        CarsGeneratorClientCharacteristicsAndPreferences
    ) = Field(...)


class CarsCharacter(BaseCharacter):
    name: str = Field(...)
    source: CarsSource | None = None
    paper_trace: CarsPaperTrace = Field(default_factory=CarsPaperTrace)
    demographics: CarsDemographics = Field(default_factory=CarsDemographics)
    persona: str = ""
    background: str = ""
    main_cognitive_conceptualization_diagram: (
        MainCognitiveConceptualizationDiagram
    ) = Field(...)
    session_specific_cognitive_conceptualization_diagram: (
        SessionSpecificCognitiveConceptualizationDiagram
    ) = Field(...)
    preferences: CarsPreferences = Field(default_factory=CarsPreferences)
    client_characteristics: CarsClientCharacteristics = Field(
        default_factory=CarsClientCharacteristics
    )
    emotion_utterance_examples: list[EmotionUtteranceExample] = Field(
        default_factory=list
    )
    example_interaction: ExampleInteraction = Field(default_factory=ExampleInteraction)
    example_state_update: ExampleStateUpdate = Field(default_factory=ExampleStateUpdate)
    initial_emotion_state: int = Field(default=50, ge=0, le=100)


class CarsResponseState(BaseModel):
    thinking: str = Field(
        description=(
            "Step-by-step CARS reasoning about topic, CCD trigger, "
            "resistance, and response."
        )
    )
    emotion: int = Field(
        description="Signed change in the client's emotion state for this turn."
    )
    intention: str = Field(description="The client's current feeling and interaction goal.")
    nonverbal_behavior: str = Field(description="The client's current nonverbal behavior.")
    response: str = Field(description="Final client response shown to the counselor.")
