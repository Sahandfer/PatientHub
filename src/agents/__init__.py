from .base import BaseAgent
from .clients import get_client

# from .evaluators import get_evaluator
from .therapists import get_therapist


def get_agent(
    agent_category: str,
    agent_type: str,
    model_client,
    lang: str,
    data: dict = None,
):
    if agent_category == "client":
        return get_client(agent_type, model_client=model_client, lang=lang, data=data)
    # elif agent_category == "evaluator":
    #     return get_evaluator(agent_type, model_client=model_client)
    elif agent_category == "therapist":
        return get_therapist(
            agent_type, model_client=model_client, lang=lang, data=data
        )
    else:
        raise ValueError(f"Unknown agent category: {agent_category}")


__all__ = ["BaseAgent", "get_agent"]
