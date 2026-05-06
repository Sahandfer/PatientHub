from pydantic import BaseModel, ConfigDict


class BaseCharacter(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
