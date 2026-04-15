"""Minimal example for adapting a character between client formats.

Usage:
    uv run python -m examples.adapter source_client=patientPsi target_client=annaAgent
"""

import hydra
from omegaconf import DictConfig
from hydra.core.config_store import ConfigStore

from patienthub.adapters import AdapterConfig, CharacterAdapter


cs = ConfigStore.instance()
cs.store(name="adapter", node=AdapterConfig)


@hydra.main(version_base=None, config_name="adapter")
def adapt(configs: DictConfig):
    adapter = CharacterAdapter(configs)
    payload = adapter.adapt()
    output_path = adapter.save(payload)
    print(f"> Saved adapted character to: {output_path}")


if __name__ == "__main__":
    adapt()
