# coding=utf-8
# Licensed under the MIT License;

"""Shared adapter schema primitives."""

from typing import Type

from pydantic import BaseModel, ConfigDict


class CharacterModel(BaseModel):
    """Base character model used by adapter schemas."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


CharacterModelType = Type[BaseModel]
