from .activeListening import ActiveListeningEvaluator, ActiveListeningEvaluatorConfig
from .cbt import CBTEvaluator, CBTEvaluatorConfig

# Registry of therapist evaluator implementations
EVALUATORS = {
    "activeListening": ActiveListeningEvaluator,
    "cbt": CBTEvaluator,
}

# Registry of therapist evaluator configs
THERAPIST_EVALUATOR_CONFIG_REGISTRY = {
    "activeListening": ActiveListeningEvaluatorConfig,
    "cbt": CBTEvaluatorConfig,
}


def get_therapist_evaluator(configs):
    eval_type = configs.eval_type
    print(f"Loading therapist evaluator agent for {eval_type}...")
    if eval_type in EVALUATORS:
        return EVALUATORS[eval_type](configs)
    else:
        raise ValueError(f"Unknown therapist evaluator type: {eval_type}")


__all__ = [
    "ActiveListeningEvaluator",
    "ActiveListeningEvaluatorConfig",
    "CBTEvaluator",
    "CBTEvaluatorConfig",
    "THERAPIST_EVALUATOR_CONFIG_REGISTRY",
    "get_therapist_evaluator",
]
