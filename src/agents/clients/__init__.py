from .basic import BasicClient
from .patientPsi import PatientPsiClient
from .roleplayDoh import RoleplayDohClient
from langchain_core.language_models import BaseChatModel

# from .patientPsi import PatientPsiClient


def get_client(agent_type: str, model_client: BaseChatModel = None, data: dict = None):
    print(f"Loading {agent_type} client agent...")
    if agent_type == "basic":
        return BasicClient(model_client=model_client, data=data)
    elif agent_type == "patientPsi":
        return PatientPsiClient(model_client=model_client, data=data)
    elif agent_type == "roleplayDoh":
        return RoleplayDohClient(model_client=model_client, data=data)
    else:
        raise ValueError(f"Unknown client agent type: {agent_type}")


__all__ = [
    "BasicClient",
    "PatientPsiClient",
    "RoleplayDohClient",
]
