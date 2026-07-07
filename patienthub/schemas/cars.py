from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter


class CarsDemographics(BaseModel):
    age: str | None = None
    occupation: str | None = None
    gender: str | None = None


class MainCognitiveConceptualizationDiagram(BaseModel):
    name: str = Field(...)
    relevant_history: str = ""
    core_beliefs: list[str] = Field(default_factory=list)
    intermediate_beliefs: list[str] = Field(default_factory=list)
    coping_strategies: list[str] = Field(default_factory=list)


class CarsAutomaticThought(BaseModel):
    situation: str = Field(...)
    cognition: str = Field(...)
    reaction: str = Field(...)


class CarsIntermediateBelief(BaseModel):
    attitude: str = Field(...)
    rule: str = Field(...)
    assumption: str = Field(...)


class SessionSpecificCognitiveConceptualizationDiagram(BaseModel):
    theme: str = ""
    structured_cbt_strategy: str = ""
    automatic_thought: CarsAutomaticThought = Field(...)
    intermediate_belief: CarsIntermediateBelief = Field(...)
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


class CarsCognitivePatternGenerationOutput(BaseModel):
    """CARS cognitive-pattern output in the final runtime character shape."""

    background: str = Field(...)
    session_specific_cognitive_conceptualization_diagram: (
        SessionSpecificCognitiveConceptualizationDiagram
    ) = Field(...)
    preferences: CarsPreferences = Field(...)
    client_characteristics: CarsClientCharacteristics = Field(...)


class CarsDialogueTurn(BaseModel):
    role: str = Field(...)
    content: str = Field(...)


class CarsSeed(BaseModel):
    main_ccd: MainCognitiveConceptualizationDiagram = Field(...)
    mesc_sentences: list[str] = Field(..., min_length=1)
    dialogue_excerpt: list[CarsDialogueTurn] = Field(...)


class CarsCharacter(BaseCharacter):
    name: str = Field(...)
    demographics: CarsDemographics = Field(default_factory=CarsDemographics)
    persona: CarsPersonaGenerationOutput = Field(...)
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
