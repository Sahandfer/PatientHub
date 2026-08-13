from pydantic import BaseModel, Field

from patienthub.schemas.base import BaseCharacter, ConvTurn


class MainCCD(BaseModel):
    name: str = Field(...)
    relevant_history: str = ""
    core_beliefs: list[str] = Field(default_factory=list)
    intermediate_beliefs: list[str] = Field(default_factory=list)
    coping_strategies: list[str] = Field(default_factory=list)


class AutomaticThought(BaseModel):
    situation: str = Field(...)
    cognition: str = Field(...)
    reaction: str = Field(...)


class IntermediateBelief(BaseModel):
    attitude: str = Field(...)
    rule: str = Field(...)
    assumption: str = Field(...)


class SessionCCD(BaseModel):
    theme: str = ""
    structured_cbt_strategy: str = ""
    automatic_thought: AutomaticThought = Field(...)
    intermediate_belief: IntermediateBelief = Field(...)
    resistance_triggers: list[str] = Field(...)


class Preferences(BaseModel):
    positive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)


class ClientCharacteristics(BaseModel):
    possible_responses_under_different_emotions: list[str] = Field(default_factory=list)
    other_client_characteristics: list[str] = Field(default_factory=list)


class PersonaGenerationOutput(BaseModel):
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


class CognitivePatternGenerationOutput(BaseModel):
    """CARS cognitive-pattern output in the final runtime character shape."""

    background: str = Field(...)
    session_ccd: SessionCCD = Field(...)
    preferences: Preferences = Field(...)
    client_characteristics: ClientCharacteristics = Field(...)


class Response(BaseModel):
    thinking: str = Field(
        description="Step-by-step reasoning about topic, CCD trigger, resistance, and response."
    )
    emotion: int = Field(
        description="Signed change in the client's emotion state for this turn."
    )
    intention: str = Field(
        description="The client's current feeling and interaction goal."
    )
    nonverbal_behavior: str = Field(
        description="The client's current nonverbal behavior."
    )
    content: str = Field(description="The client response shown to the counselor.")


class CarsCharacter(BaseCharacter):
    name: str = Field(...)
    persona: PersonaGenerationOutput = Field(...)
    background: str = Field(...)
    main_ccd: MainCCD = Field(...)
    session_ccd: SessionCCD = Field(...)
    preferences: Preferences = Field(...)
    client_characteristics: ClientCharacteristics = Field(...)


class CarsSeed(BaseModel):
    main_ccd: MainCCD = Field(...)
    mesc_sentences: list[str] = Field(..., min_length=3)
    dialogue_excerpt: list[ConvTurn] = Field(...)
