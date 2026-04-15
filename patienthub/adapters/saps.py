# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for SAPS characters."""

from .base import CharacterModel


class SAPSCharacter(CharacterModel):
    id: int | str | None = None
    name: str = "SAPSClient"
    patient_info: str
