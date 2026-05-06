from pydantic import Field

from patienthub.schemas.base import BaseCharacter


class PatientPsiCharacter(BaseCharacter):
    name: str = Field(...)
    history: str = Field(...)
    helpless_belief: list[str] = Field(...)
    unlovable_belief: list[str] = Field(...)
    worthless_belief: list[str] = Field(...)
    intermediate_belief: str = Field(...)
    intermediate_belief_depression: str = Field(...)
    coping_strategies: str = Field(...)
    situation: str = Field(...)
    auto_thought: list[str] | str = Field(...)
    emotion: list[str] = Field(...)
    behavior: list[str] | str = Field(...)
