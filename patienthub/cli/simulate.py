# coding=utf-8
# Licensed under the MIT License;

"""
Simulate therapy session(s) between a client and a therapist.

Usage:
    # Single session (defaults)
    patienthub simulate client=patientPsi therapist=user

    # One session per character in the client's data file
    patienthub simulate client=deprofile client.data_idx=-1

    # Every character, 3 runs each
    patienthub simulate client=deprofile client.data_idx=-1 num_sessions=3

    # Override config fields / add an evaluator
    patienthub simulate client.temperature=0.5 event.max_turns=50 evaluator=conv_judge

    # Language and verbose logging (DEBUG level)
    patienthub simulate lang=zh verbose=true

Logs are saved to logs/simulate_<timestamp>.log.
"""

import os
from dataclasses import dataclass, field
from typing import Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import hydra
from omegaconf import DictConfig, MISSING, OmegaConf
from hydra.core.config_store import ConfigStore

from patienthub.utils import load_json
from patienthub.events import get_event, register_event_configs
from patienthub.clients import get_client, register_client_configs
from patienthub.therapists import get_therapist, register_therapist_configs
from patienthub.evaluators import get_evaluator, register_evaluator_configs
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class SimulateConfig:
    """Main configuration for simulation."""

    defaults: List[Any] = field(
        default_factory=lambda: [
            "_self_",
            {"client": "patientPsi"},
            {"therapist": "user"},
            {"event": "therapy_session"},
            {"evaluator": None},
        ]
    )
    client: Any = MISSING
    therapist: Any = MISSING
    event: Any = MISSING
    evaluator: Optional[Any] = None
    num_sessions: int = 1
    num_workers: int = 1
    resume: bool = False
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="simulate", node=SimulateConfig)
register_client_configs(cs)
register_therapist_configs(cs)
register_evaluator_configs(cs)
register_event_configs(cs)


def run_session(configs: DictConfig) -> None:
    """Build fresh client/therapist/evaluator/event and run one session."""
    client = get_client(
        agent_name=configs.client.agent_name,
        configs=configs.client,
        lang=configs.lang,
    )
    therapist = get_therapist(
        agent_name=configs.therapist.agent_name,
        configs=configs.therapist,
        lang=configs.lang,
    )
    evaluator = (
        get_evaluator(
            agent_name=configs.evaluator.agent_name,
            configs=configs.evaluator,
            lang=configs.lang,
        )
        if configs.evaluator
        else None
    )
    event = get_event(event_name=configs.event.event_type, configs=configs.event)
    event.set_characters(
        {"client": client, "therapist": therapist, "evaluator": evaluator}
    )
    event.start()


def resolve_character_indices(client_cfg: DictConfig) -> list[int]:
    """Character indices to simulate. ``data_idx=-1`` -> every character."""
    data_idx = int(client_cfg.get("data_idx", 0))
    if data_idx != -1:
        return [data_idx]
    data_path = client_cfg.get("data_path")
    characters = load_json(data_path) if data_path else None
    if not isinstance(characters, list) or not characters:
        raise ValueError(
            "client.data_idx=-1 requires the client's data_path to be a "
            "non-empty JSON list of characters."
        )
    return list(range(len(characters)))


def session_output_path(configs: DictConfig, char_idx: int, run: int, is_batch: bool):
    """Per-session output path (own file per session when batching)."""
    if not is_batch:
        return configs.event.output_dir
    out_dir = os.path.dirname(configs.event.output_dir)
    return os.path.join(out_dir, f"{configs.client.agent_name}_c{char_idx}_r{run}.json")


def run_batch(configs: DictConfig) -> tuple[int, int]:
    """Run all (character x num_sessions) sessions. Returns (succeeded, failed)."""
    num_sessions = max(1, int(configs.num_sessions))
    num_workers = max(1, int(configs.num_workers))
    resume = bool(configs.resume)
    char_indices = resolve_character_indices(configs.client)
    total = len(char_indices) * num_sessions
    is_batch = total > 1

    logger.info(
        "Starting simulation: client=%s therapist=%s evaluator=%s event=%s "
        "lang=%s sessions=%d num_workers=%d",
        configs.client.agent_name,
        configs.therapist.agent_name,
        configs.evaluator.agent_name if configs.evaluator else None,
        configs.event.event_type,
        configs.lang,
        total,
        num_workers,
    )

    # Build the pending session specs, applying the resume (file-exists) skip.
    specs, kept = [], 0
    for char_idx in char_indices:
        for run in range(num_sessions):
            out_path = session_output_path(configs, char_idx, run, is_batch)
            if resume and os.path.exists(out_path):
                kept += 1
                continue
            specs.append((char_idx, run, out_path))

    def worker(char_idx: int, run: int, out_path: str) -> None:
        # Each worker gets its OWN config copy (no shared mutation across threads).
        cfg = OmegaConf.create(OmegaConf.to_container(configs, resolve=True))
        cfg.client.data_idx = char_idx
        cfg.event.output_dir = out_path
        run_session(cfg)

    succeeded, failed = 0, 0
    executor = ThreadPoolExecutor(max_workers=num_workers)
    futures = {executor.submit(worker, c, r, p): (c, r, p) for c, r, p in specs}
    try:
        for future in as_completed(futures):
            char_idx, run, out_path = futures[future]
            try:
                future.result()
                succeeded += 1
                logger.info(
                    "Session done (char=%d run=%d) -> %s", char_idx, run, out_path
                )
            except Exception as e:  # keep the batch going
                failed += 1
                logger.error("Session (char=%d run=%d) failed: %s", char_idx, run, e)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    if is_batch:
        logger.info(
            "Simulation complete: %d succeeded, %d failed, %d kept (out dir: %s).",
            succeeded,
            failed,
            kept,
            os.path.dirname(configs.event.output_dir),
        )
    return succeeded, failed


@hydra.main(version_base=None, config_name="simulate")
def simulate(configs: DictConfig) -> None:
    init_logging(
        "simulate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )
    try:
        run_batch(configs)
    except KeyboardInterrupt:
        logger.warning(
            "Interrupted; finished sessions are saved. Re-run with resume=true "
            "to run the rest."
        )
    except ValueError as e:
        logger.error("Simulation error: %s", e)
        return


if __name__ == "__main__":
    simulate()
