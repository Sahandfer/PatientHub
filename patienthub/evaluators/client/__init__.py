from .conv import ConvEvaluator, ConvEvaluatorConfig

# Registry of client evaluator implementations
EVALUATORS = {
    "conv": ConvEvaluator,
}

# Registry of client evaluator configs
CLIENT_EVALUATOR_CONFIG_REGISTRY = {
    "conv": ConvEvaluatorConfig,
}


def get_client_evaluator(configs):
    eval_type = configs.eval_type
    print(f"Loading {eval_type} evaluator agent...")
    if eval_type in EVALUATORS:
        return EVALUATORS[eval_type](configs)
    else:
        raise ValueError(f"Unknown evaluator type: {eval_type}")


__all__ = [
    "ConvEvaluator",
    "ConvEvaluatorConfig",
    "CLIENT_EVALUATOR_CONFIG_REGISTRY",
    "get_client_evaluator",
]
