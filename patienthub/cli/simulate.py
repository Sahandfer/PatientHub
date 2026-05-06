"""
An example for simulating a therapy session between a client and a therapist.
It requires:
    - A client agent
    - A therapist agent
    - (Optional) An evaluator agent
It creates a TherapySession object and runs the simulation using Burr.

Usage:
    # Run with defaults
    uv run python -m examples.simulate

    # Override client/therapist
    uv run python -m examples.simulate client=patientPsi therapist=basic

    # Override specific config values
    uv run python -m examples.simulate client.temperature=0.5 session.max_turns=50

    # Enable verbose logging (DEBUG level)
    uv run python -m examples.simulate verbose=true

Logs are saved to logs/simulate_<timestamp>.log.
"""

from typing import Optional

import hydra
from dataclasses import dataclass
from omegaconf import DictConfig
from hydra.core.config_store import ConfigStore

from patienthub.events import get_event
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.evaluators import get_evaluator
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)


@dataclass
class SimulateConfig:
    """Main configuration for simulation."""

    client: str = "patientPsi"
    therapist: str = "basic"
    evaluator: Optional[str] = None
    event: str = "therapy_session"
    lang: str = "en"
    verbose: bool = False


# Register all dataclass configs with Hydra before main

cs = ConfigStore.instance()
cs.store(name="simulate", node=SimulateConfig)


@hydra.main(version_base=None, config_name="simulate")
def simulate(configs: DictConfig) -> None:
    init_logging(
        "simulate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )

    logger.info(
        f"Starting simulation with {", ".join(f"{k}={v}" for k, v in configs.items())}"
    )

    try:
        # Load client
        client = get_client(agent_name=configs.client, lang=configs.lang)

        # Load therapist
        therapist = get_therapist(agent_name=configs.therapist, lang=configs.lang)

        # Load evaluator (if any)
        evaluator = (
            get_evaluator(agent_name=configs.evaluator, lang=configs.lang)
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
    except KeyboardInterrupt:
        logger.warning("Simulation interrupted by user.")
    except ValueError as e:
        logger.error(f"Simulation error: {e}")
        return


if __name__ == "__main__":
    simulate()
