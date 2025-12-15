from .schemas import get_feedback_schema
from .basic import BasicEvaluator
from omegaconf import DictConfig

EVALUATORS = {
    "basic": BasicEvaluator,
    # "cbt": CBTEvaluator,
    # "active_listening": ActiveListeningEvaluator,
}


def get_evaluator(configs: DictConfig):
    agent_type = configs.agent_type
    eval_type = configs.eval_type
    print(f"Loading {agent_type} evaluator agent for {eval_type}...")
    feedback_schema = get_feedback_schema(eval_type=eval_type)
    if agent_type in EVALUATORS:
        return EVALUATORS[agent_type](configs=configs, feedback_schema=feedback_schema)
    else:
        raise ValueError(f"Unknown evaluator type: {agent_type}")


__all__ = [
    "BasicEvaluator",
    # "ActiveListeningEvaluator",
]
