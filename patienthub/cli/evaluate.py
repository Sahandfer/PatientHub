# coding=utf-8
# Licensed under the MIT License;

"""
Evaluate simulated conversations or character profiles (batch-capable).

Usage:
    # Evaluate a directory of session files
    patienthub evaluate input_dir=data/sessions/default

    # Evaluate one file (a list of sessions), 4 workers, custom output
    patienthub evaluate input_dir=data/sessions input_name=all.json \
        output_dir=data/evaluations output_name=all_results.json num_workers=4

    # Pick an evaluator + override its config
    patienthub evaluate evaluator=profile_judge evaluator.temperature=0

    # Re-run only failed/missing sessions, merged into the existing output
    patienthub evaluate input_dir=data/sessions/default resume=true

    # Enable verbose logging (DEBUG level)
    patienthub evaluate verbose=true

Logs are saved to logs/evaluate_<timestamp>.log.
"""

import os
import glob
from dataclasses import dataclass, field
from typing import Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    input_dir: str = "data/sessions"
    input_name: str = ""
    output_dir: str = "data/evaluations"
    output_name: str = "evaluation_results.json"
    num_workers: int = 1
    resume: bool = False
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="evaluate", node=EvaluateConfig)
register_evaluator_configs(cs)


class Evaluator:
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.agent_name = configs.evaluator.agent_name
        self.evaluator = get_evaluator(
            agent_name=self.agent_name, configs=configs.evaluator, lang=configs.lang
        )
        self.sessions = self.load_sessions()

    def load_sessions(self) -> list[tuple[str, Any]]:
        """Resolve the input into a list of (session_id, session_data) pairs."""
        path = self.configs.input_dir
        file_name = self.configs.input_name
        if file_name:
            file_path = os.path.join(path, file_name)
            data = load_json(file_path)
            stem = os.path.splitext(file_name)[0]
            if isinstance(data, list):
                return [(f"{stem}_{i}", item) for i, item in enumerate(data)]
            return [(stem, data)]
        if os.path.isdir(path):
            files = sorted(glob.glob(os.path.join(path, "*.json")))
            if not files:
                raise FileNotFoundError(
                    f"No .json session files found in directory: {path}"
                )
            return [
                (os.path.splitext(os.path.basename(f))[0], load_json(f)) for f in files
            ]
        raise FileNotFoundError(f"Input path not found: {path}")

    def evaluate_worker(
        self, index: int, session_id: str, data: Any
    ) -> tuple[int, str, dict | None]:
        """Evaluate one session. Returns (index, session_id, result-or-None)."""
        total = len(self.sessions)
        logger.info("Evaluating session %d/%d (%s)", index + 1, total, session_id)
        try:
            res = self.evaluator.evaluate(data=data)
            logger.info("Session %d/%d (%s) done.", index + 1, total, session_id)
            return index, session_id, res
        except Exception as e:
            logger.error("Error evaluating session '%s': %s", session_id, e)
            return index, session_id, None

    def run_evaluate(self):
        num_workers = max(1, int(self.configs.num_workers))
        output_path = os.path.join(self.configs.output_dir, self.configs.output_name)

        done: dict[str, dict] = {}
        if self.configs.resume and os.path.exists(output_path):
            done = {r["session_id"]: r for r in load_json(output_path)}
        pending = [
            (i, sid, data)
            for i, (sid, data) in enumerate(self.sessions)
            if sid not in done
        ]
        logger.info(
            "Starting evaluation: evaluator=%s, sessions=%d, kept=%d, pending=%d, "
            "num_workers=%d",
            self.agent_name,
            len(self.sessions),
            len(done),
            len(pending),
            num_workers,
        )

        new: dict[str, dict] = {}
        succeeded = skipped = failed = 0

        def checkpoint() -> None:
            merged = [done.get(sid) or new.get(sid) for sid, _ in self.sessions]
            save_json([r for r in merged if r is not None], output_path, overwrite=True)

        executor = ThreadPoolExecutor(max_workers=num_workers)
        futures = [
            executor.submit(self.evaluate_worker, i, sid, data)
            for i, sid, data in pending
        ]
        try:
            for future in as_completed(futures):
                _, session_id, res = future.result()
                if res is None:  # evaluator raised
                    failed += 1
                elif not res:  # empty result, e.g. a session with no messages
                    skipped += 1
                else:
                    succeeded += 1
                    new[session_id] = {"session_id": session_id, "evaluation": res}
                checkpoint()
        finally:
            # On interrupt, drop queued work instead of waiting; always flush.
            executor.shutdown(wait=False, cancel_futures=True)
            checkpoint()

        logger.info(
            "Evaluation complete: %d succeeded, %d skipped, %d failed, %d kept. "
            "Saved to '%s'.",
            succeeded,
            skipped,
            failed,
            len(done),
            output_path,
        )


@hydra.main(version_base=None, config_name="evaluate")
def evaluate(configs: DictConfig):
    init_logging(
        "evaluate", level=LogLevel.DEBUG if configs.verbose else LogLevel.INFO
    )
    try:
        evaluator = Evaluator(configs)
        evaluator.run_evaluate()
    except KeyboardInterrupt:
        logger.warning(
            "Interrupted; progress saved. Re-run with resume=true to finish the rest."
        )
    except (FileNotFoundError, ValueError) as e:
        logger.error("Evaluation error: %s", e)


if __name__ == "__main__":
    evaluate()
