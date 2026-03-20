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
    uv run python -m examples.simulate client=patientPsi therapist=basic

    # Override specific config values
    uv run python -m examples.simulate client.temperature=0.5 session.max_turns=50
"""

import hydra

from typing import Optional
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.events import get_event
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.evaluators import get_evaluator


@dataclass
class SimulateConfig:
    """Main configuration for simulation."""

    client: str = "patientPsi"
    therapist: str = "basic"
    evaluator: Optional[str] = ""
    event: str = "therapy_session"
    lang: str = "en"


# Register all dataclass configs with Hydra before main

cs = ConfigStore.instance()
cs.store(name="simulate", node=SimulateConfig)


@hydra.main(version_base=None, config_name="simulate")
def simulate(configs: DictConfig) -> None:
    lang = configs.lang

    # Load client
    client = get_client(agent_name=configs.client, lang=lang)

    # Load therapist
    therapist = get_therapist(agent_name=configs.therapist, lang=lang)

    # Load evaluator (if any)
    evaluator = (
        get_evaluator(agent_name=configs.evaluator, lang=lang)
        if configs.evaluator
        else None
    )

    # # Create therapy session
    event = get_event(event_name=configs.event)
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
