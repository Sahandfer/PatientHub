from .basic import BasicClient
from .patientPsi import PatientPsiClient
from .roleplayDoh import RoleplayDohClient
from .eeyore import EeyoreClient
from .psyche import PsycheClient
from .simPatient import SimPatientClient
from .consistentMI import ConsistentMIClient
from .difyTest import DifyTestClient
from .user import UserClient

from omegaconf import DictConfig

CLIENTS = {
    "basic": BasicClient,
    "patientPsi": PatientPsiClient,
    "roleplayDoh": RoleplayDohClient,
    "eeyore": EeyoreClient,
    "psyche": PsycheClient,
    "SimPatient": SimPatientClient,
    "consistentMI": ConsistentMIClient,
    "difyTest": DifyTestClient,
    "user": UserClient,
}


def get_client(configs: DictConfig):
    agent_type = configs.agent_type
    print(f"Loading {agent_type} client agent...")
    if agent_type in CLIENTS:
        return CLIENTS[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown client agent type: {agent_type}")


__all__ = [
    "BasicClient",
    "PatientPsiClient",
    "RoleplayDohClient",
    "EeyoreClient",
    "PsycheClient",
    "SimPatientClient",
    "ConsistentMIClient",
    "DifyTestClient",
    "UserClient",
]
