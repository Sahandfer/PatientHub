from .cbt import CBTEvaluator
from .active_listening import ActiveListeningEvaluator
from langchain_core.language_models import BaseChatModel


def get_evaluator(agent_type: str, model_client: BaseChatModel = None):
    print(f"Loading {agent_type} evaluator agent...")
    if agent_type == "cbt":
        return CBTEvaluator(model_client=model_client)
    elif agent_type == "active_listening":
        return ActiveListeningEvaluator(model_client=model_client)
    else:
        raise ValueError(f"Unknown evaluator agent type: {agent_type}")


__all__ = [
    "CBTEvaluator",
    "ActiveListeningEvaluator",
]
