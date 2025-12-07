from .basic import BasicClient
from .patientPsi import PatientPsiClient
from .roleplayDoh import RoleplayDohClient
from .THU import THUClient
from .eeyore import EeyoreClient
from .psyche import psycheClient
from .SimPatient import SimPatientClient

from omegaconf import DictConfig
from langchain_core.language_models import BaseChatModel


def get_client(configs: DictConfig):
    agent_type = configs.agent_type
    print(f"Loading {agent_type} client agent...")
    if agent_type == "basic":
        return BasicClient(configs=configs)
    elif agent_type == "patientPsi":
        return PatientPsiClient(configs=configs)
    elif agent_type == "roleplayDoh":
        return RoleplayDohClient(configs=configs)
    elif agent_type == "thu":
        return THUClient(configs=configs)
    elif agent_type == "eeyore":
        return EeyoreClient(configs=configs)
    elif agent_type == 'psyche':
        return psycheClient(configs=configs)
    elif agent_type == 'SimPatient':
        return SimPatientClient(configs=configs)
    else:
        raise ValueError(f"Unknown client agent type: {agent_type}")


__all__ = [
    "BasicClient",
    "PatientPsiClient",
    "RoleplayDohClient",
    "THUClient",
    "EeyoreClient",
]
