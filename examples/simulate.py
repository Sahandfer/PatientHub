"""
An example for simulating a therapy session between a client and a therapist.
It requires:
    - A client agent
    - A therapist agent
    - (Optional) An evaluator agent
It creates a TherapySession object and runs the simulation using LangGraph.
The configurations for the session and agents are specified in the `configs/simulate.yaml` file.

Usage:
    # Run with defaults
    uv run python -m examples.simulate

    # Override client/therapist
    uv run python -m examples.simulate client=patientPsi therapist=CBT

    # Override specific config values
    uv run python -m examples.simulate client.temperature=0.5 session.max_turns=50
"""

import hydra

from typing import Any, List, Optional
from dataclasses import dataclass, field
from omegaconf import DictConfig, MISSING

from patienthub.events import get_event
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.evaluators import get_evaluator
from patienthub.configs import register_configs

DEFAULTS = [
    "_self_",
    {"client": "psyche"},
    {"therapist": "user"},
    # {"evaluator": "inspect"},
    {"event": "therapySession"},
]


@dataclass
class SimulateConfig:
    """Main configuration for simulation."""

    defaults: List[Any] = field(default_factory=lambda: DEFAULTS)
    client: Any = MISSING
    therapist: Any = MISSING
    evaluator: Optional[Any] = None
    event: Any = MISSING
    lang: str = "en"


# Register all dataclass configs with Hydra before main
register_configs("simulate", SimulateConfig)


@hydra.main(version_base=None, config_name="simulate")
def simulate(configs: DictConfig) -> None:
    lang = configs.lang

    # Load client
    client = get_client(configs=configs.client, lang=lang)

    # Load therapist
    therapist = get_therapist(configs=configs.therapist, lang=lang)

    # Load evaluator (if any)
    evaluator = None
    if configs.evaluator:
        evaluator = get_evaluator(configs=configs.evaluator, lang=lang)

    # Create therapy session
    event = get_event(configs=configs.event)
    event.set_characters(
        {
            "client": client,
            "therapist": therapist,
            "evaluator": evaluator,
        }
    )
    event.start()


if __name__ == "__main__":
    simulate()
