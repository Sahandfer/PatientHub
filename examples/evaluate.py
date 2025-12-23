"""
An example for evaluation.
It requires:
    - An evaluator agent
    - Data (e.g., conversation history, profile data)

Usage:
    # Evaluate with defaults
    uv run python -m examples.evaluate

    # Override evaluator and paths
    uv run python -m examples.evaluate evaluator=cbt input_dir=data/sessions/session.json
"""

import hydra
from omegaconf import DictConfig, MISSING
from dataclasses import dataclass
from typing import Any

from patienthub.configs import register_configs
from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator


@dataclass
class EvaluateConfig:
    """Configuration for evaluation."""

    evaluator: Any = MISSING
    input_dir: str = "data/sessions/default/session.json"
    output_dir: str = "data/evaluations/default/eval.json"


register_configs("evaluate", EvaluateConfig)


@hydra.main(version_base=None, config_name="evaluate")
def evaluate(configs: DictConfig):
    evaluator = get_evaluator(configs=configs.evaluator)
    conv_data = load_json(configs.input_dir)
    res = evaluator.evaluate(data=conv_data)

    save_json(res, configs.output_dir, overwrite=True)


if __name__ == "__main__":
    evaluate()
