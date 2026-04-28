from .base import CharacterModel, CharacterModelType
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

def get_character_model(client_name: str) -> CharacterModelType:
    if client_name not in CHARACTER_MODEL_REGISTRY:
        raise ValueError(f"Unknown adapter client: {client_name}")
    return CHARACTER_MODEL_REGISTRY[client_name]


from .engine import AdapterConfig, CharacterAdapter

__all__ = [
    "AdapterConfig",
    "CharacterAdapter",
    "CharacterModel",
    "CHARACTER_MODEL_REGISTRY",
    "get_character_model",
]
