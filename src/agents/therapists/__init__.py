from .basic import BasicTherapist
from .eliza import ElizaTherapist
from .user import UserTherapist
from langchain_core.language_models import BaseChatModel


def get_therapist(
    agent_type: str, model_client: BaseChatModel = None, data: dict = None
):
    print(f"Loading {agent_type} therapist agent...")
    if agent_type == "basic":
        return BasicTherapist(model_client=model_client, data=data)
    elif agent_type == "eliza":
        return ElizaTherapist(data=data)
    elif agent_type == "user":
        # name = input("Enter your name: ")
        return UserTherapist(data={"name": "Sam"})
    else:
        raise ValueError(f"Unknown therapist agent type: {agent_type}")


__all__ = [
    "BasicTherapist",
    "ElizaTherapist",
    "UserTherapist",
]
