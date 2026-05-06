from pydantic import Field

from patienthub.schemas.base import BaseCharacter


class RoleplayDohCharacter(BaseCharacter):
    description: str = Field(...)
