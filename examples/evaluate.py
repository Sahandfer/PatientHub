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
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator, get_evaluator_config


@dataclass
class EvaluateConfig:
    """Configuration for evaluation."""

    evaluator: str = "conv_judge"
    input_dir: str = "data/sessions/default/badtherapist.json"
    output_dir: str = "data/evaluations/default/temp_cot.json"
    prompt_path: str = "data/prompts/evaluator/client_conv.yaml"
    lang: str = "en"


cs = ConfigStore.instance()
cs.store(name="evaluate", node=EvaluateConfig)


@hydra.main(version_base=None, config_name="evaluate")
def evaluate(configs: DictConfig):
    eval_configs = get_evaluator_config(configs.evaluator)
    eval_configs.prompt_path = configs.prompt_path
    evaluator = get_evaluator(
        agent_name=configs.evaluator, configs=eval_configs, lang=configs.lang
    )

    data = load_json(configs.input_dir)
    res = evaluator.evaluate(data=data)
    save_json(res, configs.output_dir, overwrite=True)


if __name__ == "__main__":
    evaluate()
