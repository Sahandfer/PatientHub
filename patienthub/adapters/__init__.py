from .base import CharacterModel, CharacterModelType, CharacterSchemaSpec
from .patientPsi import PatientPsiCharacter
from .roleplayDoh import RoleplayDohCharacter
from .eeyore import EeyoreCharacter
from .psyche import PsycheCharacter
from .simPatient import SimPatientCharacter
from .consistentMI import ConsistentMICharacter
from .clientCast import ClientCastCharacter
from .annaAgent import AnnaAgentCharacter
from .talkDep import TalkDepCharacter
from .saps import SAPSCharacter
from .adaptiveVP import AdaptiveVPCharacter


DICT_CONTAINER_CLIENTS = {
    "simPatient",
}


CHARACTER_MODEL_REGISTRY: dict[str, CharacterModelType] = {
    "patientPsi": PatientPsiCharacter,
    "roleplayDoh": RoleplayDohCharacter,
    "eeyore": EeyoreCharacter,
    "psyche": PsycheCharacter,
    "simPatient": SimPatientCharacter,
    "consistentMI": ConsistentMICharacter,
    "clientCast": ClientCastCharacter,
    "annaAgent": AnnaAgentCharacter,
    "talkDep": TalkDepCharacter,
    "saps": SAPSCharacter,
    "adaptiveVP": AdaptiveVPCharacter,
}

CHARACTER_SCHEMA_REGISTRY: dict[str, CharacterSchemaSpec] = {
    name: CharacterSchemaSpec(
        model=model,
        container="dict" if name in DICT_CONTAINER_CLIENTS else "list",
    )
    for name, model in CHARACTER_MODEL_REGISTRY.items()
}


def get_character_model(client_name: str) -> CharacterModelType:
    if client_name not in CHARACTER_MODEL_REGISTRY:
        raise ValueError(f"Unknown adapter client: {client_name}")
    return CHARACTER_MODEL_REGISTRY[client_name]


def get_character_container(client_name: str) -> str:
    if client_name not in CHARACTER_SCHEMA_REGISTRY:
        raise ValueError(f"Unknown adapter client: {client_name}")
    return CHARACTER_SCHEMA_REGISTRY[client_name].container


from .engine import AdapterConfig, CharacterAdapter

__all__ = [
    "AdapterConfig",
    "CharacterAdapter",
    "CharacterModel",
    "CharacterSchemaSpec",
    "CHARACTER_MODEL_REGISTRY",
    "CHARACTER_SCHEMA_REGISTRY",
    "get_character_container",
    "get_character_model",
]
