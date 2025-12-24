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
from omegaconf import DictConfig, MISSING
from dataclasses import dataclass, field

from patienthub.events import TherapySession
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.evaluators import get_evaluator
from patienthub.configs import register_configs

DEFAULTS = [
    "_self_",
    {"client": "annaAgent"},
    {"therapist": "user"},
]


@dataclass
class SessionConfig:
    """Configuration for a therapy session."""

    reminder_turn_num: int = 5
    max_turns: int = 30
    langfuse: bool = False
    recursion_limit: int = 1000
    output_dir: str = "data/sessions/default/session.json"


@dataclass
class SimulateConfig:
    """Main configuration for simulation."""

    defaults: List[Any] = field(default_factory=lambda: DEFAULTS)
    session: Any = field(default_factory=SessionConfig)
    client: Any = MISSING
    therapist: Any = MISSING
    evaluator: Optional[Any] = None
    lang: str = "en"


# Register all dataclass configs with Hydra before main
register_configs("simulate", SimulateConfig)


@hydra.main(version_base=None, config_name="simulate")
def simulate(configs: DictConfig) -> None:
    lang = configs.lang
    # Load client
    configs.client.lang = lang
    client = get_client(configs=configs.client)

    # Load therapist
    configs.therapist.lang = lang
    therapist = get_therapist(configs=configs.therapist)

    # Load evaluator (if any)
    evaluator = None
    if configs.evaluator is not None:
        configs.evaluator.lang = lang
        evaluator = get_evaluator(configs=configs.evaluator)

    # Create therapy session
    session = TherapySession(
        client=client, therapist=therapist, evaluator=evaluator, configs=configs.session
    )

    # # Setting up langgraph
    lg_config = {"recursion_limit": configs.session.recursion_limit}
    if configs.session.langfuse:
        from langfuse.langchain import CallbackHandler

        session_handler = CallbackHandler()
        lg_config["callbacks"] = [session_handler]

    session.graph.invoke(
        input={},
        config=lg_config,
    )


if __name__ == "__main__":
    simulate()
