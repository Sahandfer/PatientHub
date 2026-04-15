# coding=utf-8
# Licensed under the MIT License;

"""Shared adapter schema primitives."""

from dataclasses import dataclass
from typing import Literal, Type

from pydantic import BaseModel, ConfigDict


class CharacterModel(BaseModel):
    """Base character model used by adapter schemas."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


CharacterModelType = Type[BaseModel]


@dataclass(frozen=True)
class CharacterSchemaSpec:
    model: CharacterModelType
    container: Literal["list", "dict"] = "list"
