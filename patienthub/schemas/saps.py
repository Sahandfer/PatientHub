from pydantic import Field

from patienthub.schemas.base import BaseCharacter


class SAPSCharacter(BaseCharacter):
    patient_info: str = Field(...)
