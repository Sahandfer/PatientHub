# coding=utf-8
# Licensed under the MIT License;

"""
Generate patient character profile(s).

Generators are pure transformers (input record -> character object). This CLI
owns the I/O: it loads the input list, drives the loop (with optional resume and
parallelism), and saves the returned characters to ``output_path``.

Usage:
    # Item-driven generator: one character per record in an input JSON list
    patienthub generate generator=clientCast input_path=data/seeds/clientCast.json

    # Config-parameterized generator (no input list): one character from config
    patienthub generate generator=patientZero generator.disease_key=depression

    # Several samples of a config-parameterized generator, appended to the bank
    patienthub generate generator=patientZero num_samples=10

    # Custom output location + parallel workers
    patienthub generate generator=clientCast input_path=... \
        output_path=data/characters/clientCast.json num_workers=4

    # Resume: keep characters already in the output, only fill the rest
    patienthub generate generator=clientCast input_path=... resume=true

    # Language and verbose logging
    patienthub generate generator=deprofile lang=zh verbose=true

Logs are saved to logs/generate_<timestamp>.log.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Callable, List
from concurrent.futures import ThreadPoolExecutor, as_completed

import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStore

from patienthub.generators import (
    get_generator,
    register_generator_configs,
    BaseGenerator,
)
from patienthub.utils import load_json, save_json
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class GenerateConfig:
    """Configuration for generating data."""

    defaults: List[Any] = field(
        default_factory=lambda: ["_self_", {"generator": "annaAgent"}]
    )
    generator: Any = MISSING
    input_path: str = ""  # optional JSON list of input records (item-driven)
    output_path: str = ""  # defaults to data/characters/<agent_name>.json
    num_samples: int = 1  # used only when input_path is empty
    num_workers: int = 1
    resume: bool = False
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="generate", node=GenerateConfig)
register_generator_configs(cs)


def run_list(
    build: Callable[[], BaseGenerator],
    items: List[Any],
    output_path: str,
    resume: bool,
    num_workers: int,
) -> tuple[int, int, int]:
    """One character per input item, index-aligned and resume-aware.

    Each item is validated against the generator's seed schema before generation
    (see ``BaseGenerator.prepare_seed``); if that raises, the item is counted as
    failed. Returns (succeeded, failed, kept). Failed/pending slots are saved as
    ``null`` so a later ``resume`` run re-generates only those.
    """
    total = len(items)
    results: list[Any] = [None] * total
    if resume and os.path.exists(output_path):
        existing = load_json(output_path)
        if isinstance(existing, list):
            for i in range(min(len(existing), total)):
                results[i] = existing[i]
    pending = [i for i in range(total) if results[i] is None]
    kept = total - len(pending)
    succeeded = failed = 0
    if resume and kept:
        logger.info("Resuming: %d kept, %d to generate.", kept, len(pending))

    # Each worker builds its own generator: generators hold per-call state, so a
    # shared instance is not thread-safe.
    def work(i: int) -> tuple[int, Any]:
        gen = build()
        character = gen.generate_character(gen.prepare_seed(items[i]))
        return i, character.model_dump(by_alias=True, mode="json")

    executor = ThreadPoolExecutor(max_workers=num_workers)
    futures = {executor.submit(work, i): i for i in pending}
    try:
        for future in as_completed(futures):
            i = futures[future]
            try:
                _, results[i] = future.result()
                succeeded += 1
                logger.info("Generated character %d/%d.", i + 1, total)
            except Exception as e:  # keep the batch going
                failed += 1
                logger.error("Character %d/%d failed: %s", i + 1, total, e)
            save_json(results, output_path, overwrite=True)
    finally:
        # On interrupt, drop queued work instead of waiting; always flush.
        executor.shutdown(wait=False, cancel_futures=True)
        save_json(results, output_path, overwrite=True)

    return succeeded, failed, kept


def run_samples(
    build: Callable[[], BaseGenerator],
    num_samples: int,
    output_path: str,
    num_workers: int,
) -> tuple[int, int]:
    """Generate ``num_samples`` characters from config and append them to the bank."""
    # Read the existing bank up front so each checkpoint rewrites the full bank;
    # save_json is atomic, so a partial run leaves a valid appended file.
    existing: list[Any] = []
    if os.path.exists(output_path):
        prev = load_json(output_path)
        existing = prev if isinstance(prev, list) else [prev]
    records: list[Any] = []
    succeeded = failed = 0

    executor = ThreadPoolExecutor(max_workers=num_workers)
    futures = [
        executor.submit(
            lambda: build().generate_character().model_dump(by_alias=True, mode="json")
        )
        for _ in range(num_samples)
    ]
    try:
        for future in as_completed(futures):
            try:
                records.append(future.result())
                succeeded += 1
                logger.info("Generated sample %d/%d.", succeeded, num_samples)
            except Exception as e:
                failed += 1
                logger.error("Sample failed: %s", e)
            save_json(existing + records, output_path, overwrite=True)
    finally:
        # On interrupt, drop queued work instead of waiting; always flush.
        executor.shutdown(wait=False, cancel_futures=True)
        save_json(existing + records, output_path, overwrite=True)

    return succeeded, failed


@hydra.main(version_base=None, config_name="generate")
def generate(configs: DictConfig):
    init_logging(
        "generate", level=LogLevel.DEBUG if configs.verbose else LogLevel.INFO
    )
    agent_name = configs.generator.agent_name
    output_path = configs.output_path or f"data/characters/{agent_name}.json"
    num_workers = max(1, int(configs.num_workers))

    def build() -> BaseGenerator:
        return get_generator(
            agent_name=agent_name, configs=configs.generator, lang=configs.lang
        )

    logger.info(
        "Starting generation: generator=%s, lang=%s, workers=%d -> %s",
        agent_name,
        configs.lang,
        num_workers,
        output_path,
    )
    try:
        if configs.input_path:
            items = load_json(configs.input_path)
            if not isinstance(items, list):
                raise ValueError(
                    f"input_path must be a JSON list of records: {configs.input_path}"
                )
            logger.info(
                "Loaded %d record(s) from %s.", len(items), configs.input_path
            )
            succeeded, failed, kept = run_list(
                build, items, output_path, bool(configs.resume), num_workers
            )
            logger.info(
                "Generation complete: %d succeeded, %d failed, %d kept -> %s",
                succeeded,
                failed,
                kept,
                output_path,
            )
        else:
            num_samples = max(1, int(configs.num_samples))
            succeeded, failed = run_samples(
                build, num_samples, output_path, num_workers
            )
            logger.info(
                "Generation complete: %d succeeded, %d failed -> %s",
                succeeded,
                failed,
                output_path,
            )
    except KeyboardInterrupt:
        logger.warning(
            "Interrupted; progress saved to '%s'. Re-run with resume=true to "
            "finish the rest.",
            output_path,
        )
    except (FileNotFoundError, ValueError) as e:
        logger.error("Generation error: %s", e)


if __name__ == "__main__":
    generate()
