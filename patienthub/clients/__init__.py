from .patientPsi import PatientPsiClient, PatientPsiClientConfig
from .roleplayDoh import RoleplayDohClient, RoleplayDohClientConfig
from .eeyore import EeyoreClient, EeyoreClientConfig
from .psyche import PsycheClient, PsycheClientConfig
from .simPatient import SimPatientClient, SimPatientClientConfig
from .consistentMI import ConsistentMIClient, ConsistentMIClientConfig
from .user import UserClient, UserClientConfig
from .clientCast import ClientCastClient, ClientCastClientConfig
from .annaAgent import AnnaAgentClient, AnnaAgentClientConfig
from .talkDep import TalkDepClient, TalkDepClientConfig
from .saps import SAPSClient, SAPSClientConfig
from .adaptiveVP import AdaptiveVPClient, AdaptiveVPClientConfig


from omegaconf import DictConfig

# Registry of client implementations
CLIENT_REGISTRY = {
    "patientPsi": PatientPsiClient,
    "roleplayDoh": RoleplayDohClient,
    "eeyore": EeyoreClient,
    "psyche": PsycheClient,
    "simPatient": SimPatientClient,
    "consistentMI": ConsistentMIClient,
    "user": UserClient,
    "clientCast": ClientCastClient,
    "annaAgent": AnnaAgentClient,
    "talkDep": TalkDepClient,
    "saps": SAPSClient,
    "adaptiveVP": AdaptiveVPClient,
}

# Registry of client configs (for Hydra registration)
CLIENT_CONFIG_REGISTRY = {
    "patientPsi": PatientPsiClientConfig,
    "roleplayDoh": RoleplayDohClientConfig,
    "eeyore": EeyoreClientConfig,
    "psyche": PsycheClientConfig,
    "simPatient": SimPatientClientConfig,
    "consistentMI": ConsistentMIClientConfig,
    "user": UserClientConfig,
    "clientCast": ClientCastClientConfig,
    "annaAgent": AnnaAgentClientConfig,
    "talkDep": TalkDepClientConfig,
    "saps": SAPSClientConfig,
    "adaptiveVP": AdaptiveVPClientConfig,
}


def get_client(configs: DictConfig, lang: str = "en"):
    configs.lang = lang
    agent_type = configs.agent_type
    print(f"Loading {agent_type} client agent...")
    if agent_type in CLIENT_REGISTRY:
        return CLIENT_REGISTRY[agent_type](configs=configs)
    else:
        raise ValueError(f"Unknown client agent type: {agent_type}")


def register_client_configs(cs):
    for name, config_cls in CLIENT_CONFIG_REGISTRY.items():
        cs.store(group="client", name=name, node=config_cls)


__all__ = [
    "get_client",
    "register_client_configs",
]
