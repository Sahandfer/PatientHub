"""
Evaluate a simulated conversation or character profile.

Usage:
    # Evaluate with defaults
    patienthub evaluate

    # Pick an evaluator and I/O paths
    patienthub evaluate evaluator=profile_judge \
        input_dir=data/sessions/session.json output_dir=data/evaluations/out.json

    # Override evaluator config fields
    patienthub evaluate evaluator.temperature=0 \
        evaluator.prompt_path=data/prompts/evaluator/client_conv.yaml

    # Enable verbose logging (DEBUG level)
    patienthub evaluate verbose=true

Logs are saved to logs/evaluate_<timestamp>.log.
"""

from dataclasses import dataclass, field
from typing import Any, List

import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStore

from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator, register_evaluator_configs
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class EvaluateConfig:
    """Configuration for evaluation."""

    defaults: List[Any] = field(
        default_factory=lambda: ["_self_", {"evaluator": "conv_judge"}]
    )
    evaluator: Any = MISSING
    input_dir: str = "data/sessions/default/badtherapist.json"
    output_dir: str = "data/evaluations/default/temp_cot.json"
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="evaluate", node=EvaluateConfig)
register_evaluator_configs(cs)


@hydra.main(version_base=None, config_name="evaluate")
def evaluate(configs: DictConfig):
    init_logging(
        "evaluate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )
    agent_name = configs.evaluator.agent_name
    logger.info(
        "Starting evaluation: evaluator=%s, input=%s", agent_name, configs.input_dir
    )
    try:
        evaluator = get_evaluator(
            agent_name=agent_name, configs=configs.evaluator, lang=configs.lang
        )
        data = load_json(configs.input_dir)
        res = evaluator.evaluate(data=data)
        save_json(res, configs.output_dir, overwrite=True)
        logger.info("Evaluation saved to '%s'", configs.output_dir)
    except KeyboardInterrupt:
        logger.warning("Evaluation interrupted by user.")


if __name__ == "__main__":
    evaluate()
