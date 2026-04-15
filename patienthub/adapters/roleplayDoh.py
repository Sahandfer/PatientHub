# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for roleplayDoh characters."""

from .base import CharacterModel


class RoleplayDohCharacter(CharacterModel):
    name: str = "Client"
    description: str = ""
