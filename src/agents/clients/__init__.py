from .basic import BasicClient
from .patientPsi import PatientPsiClient
from .roleplayDoh import RoleplayDohClient
from .THU import THUClient
from .eeyore import EeyoreClient
from .psyche import PsycheClient
from .simPatient import SimPatientClient
from .consistentMI import ConsistentMIClient

from omegaconf import DictConfig

CLIENTS = {
    "basic": BasicClient,
    "patientPsi": PatientPsiClient,
    "roleplayDoh": RoleplayDohClient,
    "thu": THUClient,
    "eeyore": EeyoreClient,
    "psyche": PsycheClient,
    "SimPatient": SimPatientClient,
    "consistentMI": ConsistentMIClient,
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
    "THUClient",
    "EeyoreClient",
    "PsycheClient",
    "SimPatientClient",
    "ConsistentMIClient",
]
