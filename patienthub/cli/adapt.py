# coding=utf-8
# Licensed under the MIT License;

"""
Adapt character profiles from one client format to another.
It requires:
    - source_path: path to the source character JSON file
    - target_client: name of the target client (e.g., roleplayDoh)
It infers the target structure from the registered schema and can optionally use
the target client's existing character file as a few-shot example.

By default a single character (source_idx) is adapted. Set source_idx=-1 to
batch-adapt every character in the file in parallel using num_workers threads.

Usage:
    # Adapt a single character using schema only
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh

    # Pick a specific character by index
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh source_idx=2

    # Batch-adapt every character in the file with 4 workers
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh source_idx=-1 num_workers=4

    # Continue a batch run that was interrupted (resume from existing output)
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh source_idx=-1 num_workers=4 resume=true

    # Supplement with a few-shot example (the target client's existing character file)
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh use_example=true

    # Specify output directory
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh output_dir=data/characters/adapted/

    # Generate output in a different language (e.g., Chinese)
    patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh lang=zh
"""

import os
import json
import hydra
from pydantic import ValidationError
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore
from concurrent.futures import ThreadPoolExecutor, as_completed

from patienthub.configs import APIModelConfig
from patienthub.schemas import get_profile_schema
from patienthub.utils.logger import get_logger, init_logging, LogLevel
from patienthub.utils import (
    load_prompts,
    load_json,
    save_json,
    get_chat_model,
    parse_json_response,
)

logger = get_logger(__name__)


@dataclass
class AdaptConfig(APIModelConfig):
    """Configuration for adapting character profiles between client formats."""

    prompt_path: str = "data/prompts/cli/adapt.yaml"
    source_path: str = ""
    source_idx: int = 0
    target_client: str = ""
    use_example: bool = False
    output_dir: str = "data/characters/"
    resume: bool = False
    lang: str = "en"
    num_workers: int = 1


cs = ConfigStore.instance()
cs.store(name="adapt", node=AdaptConfig)
init_logging("adapt", level=LogLevel.INFO)


class Adapter:
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.prompt = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.chat_model = get_chat_model(configs)
        source_name = os.path.splitext(os.path.basename(configs.source_path))[0]
        output_name = f"{self.configs.target_client}_from_{source_name}.json"
        self.output_path = os.path.join(self.configs.output_dir, output_name)

        # Load the source data to be adapted
        self.source_data = load_json(self.configs.source_path)
        if not isinstance(self.source_data, list):
            self.source_data = [self.source_data]

        # Load the target schema for adaption
        self.target_schema = get_profile_schema(configs.target_client)
        if self.target_schema is None:
            raise ValueError(f"Unknown target client: {configs.target_client}")
        self.target_schema_json = json.dumps(
            self.target_schema.model_json_schema(), indent=2
        )
        # Load examples for few-shot (if any)
        self.target_example = None
        if configs.use_example:
            example_path = self.find_example_path(configs.target_client)
            example_data = load_json(example_path) if example_path else None
            if isinstance(example_data, list):
                example_data = example_data[0] if example_data else None
            if example_data:
                self.target_example = json.dumps(
                    example_data, indent=2, ensure_ascii=False
                )
                logger.info("Using few-shot example from '%s'", example_path)
            else:
                logger.warning(
                    "use_example=true but no usable example found for '%s'; "
                    "proceeding with schema only.",
                    configs.target_client,
                )

    @staticmethod
    def find_example_path(
        target_client: str, search_dir: str = "data/characters"
    ) -> str | None:
        """Return the reference character file for a client, or None if absent."""
        path = os.path.join(search_dir, f"{target_client}.json")
        return path if os.path.isfile(path) else None

    @staticmethod
    def extract_profile(entry: dict) -> dict:
        """Return the inner 'profile' object when present, else the entry itself."""
        if isinstance(entry, dict) and "profile" in entry:
            return entry["profile"]
        return entry

    def adapt_single_instance(
        self,
        source_character_json: str,
    ) -> dict:
        """Adapt a single character profile to the target client format."""
        prompt = self.prompt.render(
            source_character=source_character_json,
            target_schema=self.target_schema_json,
            target_example=self.target_example,
            lang=self.configs.lang,
        )
        result = self.chat_model.generate([{"role": "system", "content": prompt}])
        adapted = parse_json_response(result.content)
        try:
            validated = self.target_schema.model_validate(adapted)
            return validated.model_dump(by_alias=True, mode="json")
        except ValidationError as e:
            logger.error("Adapted output failed schema validation: %s", e)
            return None

    def adapt_worker(
        self,
        index: int,
        total: int,
        character: dict,
    ) -> tuple[int, dict]:
        """Worker function executed by each thread. Returns (index, adapted_dict)."""
        source_json = json.dumps(character, indent=2, ensure_ascii=False)
        logger.info("Adapting character %d/%d ...", index + 1, total)

        adapted = self.adapt_single_instance(source_character_json=source_json)

        logger.info("Character %d/%d done.", index + 1, total)
        return index, adapted

    def run_adapt(self):
        logger.info(
            "Starting adaptation: %s → %s (index=%d)",
            self.configs.source_path,
            self.configs.target_client,
            self.configs.source_idx,
        )
        try:
            # Single character: adapt the entry at source_idx and append to output.
            if self.configs.source_idx >= 0:
                try:
                    data = self.source_data[self.configs.source_idx]
                except IndexError:
                    logger.error(
                        "source_idx=%d is out of range (file has %d entries).",
                        self.configs.source_idx,
                        len(self.source_data),
                    )
                    return
                character = self.extract_profile(data)
                _, adapted = self.adapt_worker(
                    index=self.configs.source_idx,
                    total=len(self.source_data),
                    character=character,
                )
                if adapted is None:
                    logger.error("Adaptation failed schema validation; nothing saved.")
                    return
                save_json(adapted, self.output_path, overwrite=False)
                logger.info("Adapted character saved to '%s'", self.output_path)
                return

            # Batch: adapt every character in parallel using num_workers threads.
            profiles = [self.extract_profile(entry) for entry in self.source_data]
            total = len(profiles)
            num_workers = max(1, self.configs.num_workers)

            # Output is index-aligned (null for failed/not-yet-done). With resume,
            # seed from the existing output and re-run only the empty slots.
            results: list[dict | None] = [None] * total
            if self.configs.resume and os.path.exists(self.output_path):
                existing = load_json(self.output_path)
                if isinstance(existing, list):
                    for i in range(min(len(existing), total)):
                        results[i] = existing[i]
            pending = [i for i in range(total) if results[i] is None]
            kept = total - len(pending)
            logger.info(
                "Batch-adapting %d/%d character(s) → %s (num_workers=%d, kept=%d)",
                len(pending),
                total,
                self.configs.target_client,
                num_workers,
                kept,
            )

            succeeded, failed = 0, 0
            executor = ThreadPoolExecutor(max_workers=num_workers)
            futures = {
                executor.submit(self.adapt_worker, i, total, profiles[i]): i
                for i in pending
            }
            try:
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        i, adapted = future.result()
                        results[i] = adapted
                        if adapted is None:
                            failed += 1
                        else:
                            succeeded += 1
                    except Exception as e:
                        failed += 1
                        logger.error("Failed to adapt character %d: %s", idx + 1, e)
                    save_json(results, self.output_path, overwrite=True)
            finally:
                # On interrupt, drop queued work instead of waiting; always flush.
                executor.shutdown(wait=False, cancel_futures=True)
                save_json(results, self.output_path, overwrite=True)

            logger.info(
                "Batch adaptation complete: %d succeeded, %d failed, %d kept. "
                "Saved to '%s'.",
                succeeded,
                failed,
                kept,
                self.output_path,
            )

        except KeyboardInterrupt:
            logger.warning(
                "Interrupted; progress saved to '%s'. Re-run with resume=true "
                "to finish the rest.",
                self.output_path,
            )


@hydra.main(version_base=None, config_name="adapt")
def adapt(configs: DictConfig):
    if not configs.source_path or not configs.target_client:
        raise ValueError("source_path and target_client are required.")
    if not os.path.isfile(configs.source_path):
        raise FileNotFoundError(f"Source file not found: {configs.source_path}")
    adapter = Adapter(configs)
    adapter.run_adapt()


if __name__ == "__main__":
    adapt()
