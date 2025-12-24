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
from typing import Any, List
from dataclasses import dataclass, field
from omegaconf import DictConfig, MISSING

from patienthub.configs import register_configs
from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator

DEFAULTS = [
    "_self_",
    {"evaluator": "rating"},
]


@dataclass
class EvaluateConfig:
    """Configuration for evaluation."""

    defaults: List[Any] = field(default_factory=lambda: DEFAULTS)
    evaluator: Any = MISSING
    input_dir: str = "data/sessions/patientPsi/session_1.json"
    output_dir: str = "data/evaluations/patientPsi/session_1_rating_eval.json"
    lang: str = "en"


register_configs("evaluate", EvaluateConfig)


@hydra.main(version_base=None, config_name="evaluate")
def evaluate(configs: DictConfig):
    configs.evaluator.lang = configs.lang
    evaluator = get_evaluator(configs=configs.evaluator)

    data = load_json(configs.input_dir)
    res = evaluator.evaluate(data=data)
    save_json(res, configs.output_dir, overwrite=True)


if __name__ == "__main__":
    evaluate()
