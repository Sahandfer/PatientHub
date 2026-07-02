"""
Simulate a therapy session between a client and a therapist.

Usage:
    # Run with defaults
    patienthub simulate

    # Pick client / therapist
    patienthub simulate client=patientPsi therapist=user

    # Override config fields (e.g. temperature, session length)
    patienthub simulate client.temperature=0.5 event.max_turns=50

    # Add an (optional) evaluator
    patienthub simulate evaluator=conv_judge

    # Language and verbose logging (DEBUG level)
    patienthub simulate lang=zh verbose=true

Logs are saved to logs/simulate_<timestamp>.log.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional

import hydra
from omegaconf import DictConfig, MISSING
from hydra.core.config_store import ConfigStore

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
    lang: str = "en"
    verbose: bool = False


cs = ConfigStore.instance()
cs.store(name="simulate", node=SimulateConfig)
register_client_configs(cs)
register_therapist_configs(cs)
register_evaluator_configs(cs)
register_event_configs(cs)


@hydra.main(version_base=None, config_name="simulate")
def simulate(configs: DictConfig) -> None:
    init_logging(
        "simulate", level=LogLevel.DEBUG if configs.verbose else LogLevel.WARNING
    )
    logger.info(
        "Starting simulation: client=%s therapist=%s evaluator=%s event=%s lang=%s",
        configs.client.agent_name,
        configs.therapist.agent_name,
        configs.evaluator.agent_name if configs.evaluator else None,
        configs.event.event_type,
        configs.lang,
    )

    try:
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
