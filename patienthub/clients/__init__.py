from .base import BaseClient
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


import logging
from omegaconf import DictConfig

logger = logging.getLogger(__name__)

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


def get_client(agent_name: str, configs: DictConfig = None, lang: str = "en"):
    if agent_name not in CLIENT_REGISTRY:
        raise ValueError(f"Unknown client agent type: {agent_name}")
    if configs is None:
        configs = get_client_config(agent_name)
    configs.lang = lang
    try:
        client = CLIENT_REGISTRY[agent_name](configs=configs)
    except Exception as e:
        logger.error("Failed to initialize client '%s': %s", agent_name, e)
        raise ValueError(f"Error initializing client agent '{agent_name}'") from e
    logger.info(
        "Loaded client '%s' -> %s",
        agent_name,
        ", ".join(f"{k}={v}" for k, v in vars(configs).items()),
    )
    return client


def get_client_config(agent_name: str):
    if agent_name in CLIENT_CONFIG_REGISTRY:
        return CLIENT_CONFIG_REGISTRY[agent_name]()
    else:
        raise ValueError(f"Client config for {agent_name} not found in registry.")


def register_client_configs(cs):
    for name, config_cls in CLIENT_CONFIG_REGISTRY.items():
        cs.store(group="client_configs", name=name, node=config_cls)


__all__ = ["BaseClient", "get_client", "register_client_configs", "get_client_config"]
