"""
An example for evaluation.
It requires:
    - An evaluator agent
    - Data (e.g., conversation history, profile data)

Usage:
    # Evaluate with defaults
    uv run python -m examples.evaluate

    # Override evaluator and paths
    uv run python -m examples.evaluate evaluator=conv_judge input_dir=data/sessions/session.json

    # Enable verbose logging (DEBUG level)
    uv run python -m examples.evaluate verbose=true

Logs are saved to logs/evaluate_<timestamp>.log.
"""

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator, get_evaluator_config
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class EvaluateConfig:
    """Configuration for evaluation."""

    evaluator: str = "conv_judge"
    input_dir: str = "data/sessions/default/badtherapist.json"
    output_dir: str = "data/evaluations/default/temp_cot.json"
    prompt_path: str = "data/prompts/evaluator/client_conv.yaml"
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="evaluate", node=EvaluateConfig)


@hydra.main(version_base=None, config_name="evaluate")
def evaluate(configs: DictConfig):
    init_logging(
        "evaluate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )
    logger.info(
        "Starting evaluation: evaluator=%s, input=%s",
        configs.evaluator,
        configs.input_dir,
    )
    try:
        eval_configs = get_evaluator_config(configs.evaluator)
        eval_configs.prompt_path = configs.prompt_path
        evaluator = get_evaluator(
            agent_name=configs.evaluator, configs=eval_configs, lang=configs.lang
        )
        data = load_json(configs.input_dir)
        res = evaluator.evaluate(data=data)
        save_json(res, configs.output_dir, overwrite=True)
        logger.info("Evaluation saved to '%s'", configs.output_dir)
    except KeyboardInterrupt:
        logger.warning("Evaluation interrupted by user.")


if __name__ == "__main__":
    evaluate()
