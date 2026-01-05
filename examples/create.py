"""
A script for creating new agents.
It requires:
    - agent_type: either "client" or "therapist"
    - agent_name: the name of the new agent to be created
It creates:
- The agent implementation at `patienthub/{agent_type}s/{agent_name}.py`.
- The configuration file at `configs/{agent_type}/{agent_name}.yaml`.
- A prompt template file at `data/prompts/{agent_type}/{agent_name}.yaml`.
It also adds the new agent to the corresponding `__init__.py` file.

Usage:
    # Create a new client agent
    uv run python -m examples.create generator.gen_agent_type=client generator.gen_agent_name=myAgent

    # Create a new therapist agent
    uv run python -m examples.create generator.gen_agent_type=therapist generator.gen_agent_name=myTherapist
"""

import hydra
from omegaconf import DictConfig, MISSING
from dataclasses import dataclass, field
from typing import Any, List

from patienthub.configs import register_configs
from patienthub.generators import get_generator

DEFAULTS = [
    "_self_",
    {"generator": "agent_files"},
]


@dataclass
class CreateConfig:
    """Configuration for creating new agents."""

    defaults: List[Any] = field(default_factory=lambda: DEFAULTS)
    generator: Any = MISSING


register_configs("create", CreateConfig)


@hydra.main(version_base=None, config_name="create")
def main(configs: DictConfig) -> None:
    file_creator = get_generator(configs=configs.generator)
    file_creator.generate_files()


if __name__ == "__main__":
    main()
