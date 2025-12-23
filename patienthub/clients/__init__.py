from .basic import BasicClient, BasicClientConfig
from .patientPsi import PatientPsiClient, PatientPsiClientConfig
from .roleplayDoh import RoleplayDohClient, RoleplayDohClientConfig
from .eeyore import EeyoreClient, EeyoreClientConfig
from .psyche import PsycheClient, PsycheClientConfig
from .simPatient import SimPatientClient, SimPatientClientConfig
from .consistentMI import ConsistentMIClient, ConsistentMIClientConfig
from .difyTest import DifyTestClient, DifyTestClientConfig
from .user import UserClient, UserClientConfig
from .clientCast import ClientCastClient, ClientCastClientConfig

from omegaconf import DictConfig

# Registry of client implementations
CLIENT_REGISTRY = {
    "basic": BasicClient,
    "patientPsi": PatientPsiClient,
    "roleplayDoh": RoleplayDohClient,
    "eeyore": EeyoreClient,
    "psyche": PsycheClient,
    "simPatient": SimPatientClient,
    "consistentMI": ConsistentMIClient,
    "difyTest": DifyTestClient,
    "user": UserClient,
    "clientCast": ClientCastClient,
}

# Registry of client configs (for Hydra registration)
CLIENT_CONFIG_REGISTRY = {
    "basic": BasicClientConfig,
    "patientPsi": PatientPsiClientConfig,
    "roleplayDoh": RoleplayDohClientConfig,
    "eeyore": EeyoreClientConfig,
    "psyche": PsycheClientConfig,
    "simPatient": SimPatientClientConfig,
    "consistentMI": ConsistentMIClientConfig,
    "difyTest": DifyTestClientConfig,
    "user": UserClientConfig,
    "clientCast": ClientCastClientConfig,
}


def get_client(configs: DictConfig):
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
