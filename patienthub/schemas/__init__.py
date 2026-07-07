import logging
from .base import BaseCharacter
from .adaptiveVP import AdaptiveVPCharacter
from .annaAgent import AnnaAgentCharacter, AnnaAgentSeed
from .clientCast import ClientCastCharacter, ClientCastSeed
from .consistentMI import ConsistentMICharacter
from .eeyore import EeyoreCharacter
from .patientPsi import PatientPsiCharacter
from .patientZero import PatientZeroCharacter, PatientZeroSeed
from .psyche import PsycheCharacter, PsycheSeed
from .roleplayDoh import RoleplayDohCharacter
from .saps import SAPSCharacter
from .simPatient import SimPatientCharacter
from .talkDep import TalkDepCharacter
from .deprofile import DeprofileCharacter, DeprofileSeed

# from .patientAct import PatientActClientCharacter, GeneratedProfile

logger = logging.getLogger(__name__)

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
    "deprofile": DeprofileCharacter,
    # "patientAct": GeneratedProfile,
}

THERAPIST_SCHEMA_REGISTRY = {}


SEED_SCHEMA_REGISTRY = {
    "clientCast": ClientCastSeed,
    "psyche": PsycheSeed,
    "annaAgent": AnnaAgentSeed,
    "patientZero": PatientZeroSeed,
    "deprofile": DeprofileSeed,
}


def get_seed_schema(agent_name: str):
    """Return the seed schema for a generator, or None if it has none."""
    return SEED_SCHEMA_REGISTRY.get(agent_name)


def get_profile_schema(
    agent_name: str, agent_type: str = "client"
) -> type[BaseCharacter]:
    if agent_type == "client":
        registry = CLIENT_SCHEMA_REGISTRY
    elif agent_type == "therapist":
        registry = THERAPIST_SCHEMA_REGISTRY
    else:
        logger.warning(f"Invalid agent type: {agent_type}")
        return None

    if agent_name not in registry:
        logger.warning(
            f"Schema for '{agent_name}' not found in {agent_type}_SCHEMA_REGISTRY."
        )
        return None
    return registry[agent_name]


__all__ = [
    "BaseCharacter",
    "CLIENT_SCHEMA_REGISTRY",
    "THERAPIST_SCHEMA_REGISTRY",
    "SEED_SCHEMA_REGISTRY",
    "get_profile_schema",
    "get_seed_schema",
]
