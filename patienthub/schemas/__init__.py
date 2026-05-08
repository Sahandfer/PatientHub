from .base import BaseCharacter
from .adaptiveVP import AdaptiveVPCharacter
from .annaAgent import AnnaAgentCharacter
from .clientCast import ClientCastCharacter
from .consistentMI import ConsistentMICharacter
from .eeyore import EeyoreCharacter
from .patientPsi import PatientPsiCharacter
from .patientZero import PatientZeroCharacter
from .psyche import PsycheCharacter
from .roleplayDoh import RoleplayDohCharacter
from .saps import SAPSCharacter
from .simPatient import SimPatientCharacter
from .talkDep import TalkDepCharacter

CLIENT_SCHEMA_REGISTRY = {
    "patientPsi": PatientPsiCharacter,
    "patientZero": PatientZeroCharacter,
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


def get_profile_schema(agent_name: str) -> type[BaseCharacter]:
    if agent_name not in CLIENT_SCHEMA_REGISTRY:
        raise ValueError(f"Schema for '{agent_name}' not found in registry.")
    return CLIENT_SCHEMA_REGISTRY[agent_name]


__all__ = [
    "BaseCharacter",
    "AdaptiveVPCharacter",
    "AnnaAgentCharacter",
    "ClientCastCharacter",
    "ConsistentMICharacter",
    "EeyoreCharacter",
    "PatientPsiCharacter",
    "PatientZeroCharacter",
    "PsycheCharacter",
    "RoleplayDohCharacter",
    "SAPSCharacter",
    "SimPatientCharacter",
    "TalkDepCharacter",
    "CLIENT_SCHEMA_REGISTRY",
    "get_profile_schema",
]
