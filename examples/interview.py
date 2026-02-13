import hydra

from typing import Any, List, Optional
from omegaconf import DictConfig, MISSING
from dataclasses import dataclass, field

from patienthub.events import get_event
from patienthub.clients import get_client
from patienthub.evaluators import get_evaluator
from patienthub.configs import register_configs

DEFAULTS = [
    "_self_",
    {"client": "patientPsi"},
    {"evaluator": "llm_judge"},
    {"event": "therapySession"},
]


@dataclass
class InterviewConfig:
    """Main configuration for simulation."""

    defaults: List[Any] = field(default_factory=lambda: DEFAULTS)
    client: Any = MISSING
    evaluator: Optional[Any] = None
    event: Any = MISSING
    lang: str = "en"


# Register all dataclass configs with Hydra before main
register_configs("interview", InterviewConfig)


@hydra.main(version_base=None, config_name="interview")
def interview(configs: DictConfig) -> None:
    lang = configs.lang

    # Load client
    interviewee = get_client(configs=configs.client, lang=lang)

    # Load evaluator (if any)
    interviewer = get_evaluator(configs=configs.evaluator, lang=lang)

    # Create therapy session
    event = get_event(configs=configs.event)
    event.set_characters(
        {
            "interviewee": interviewee,
            "interviewer": interviewer,
        }
    )
    # event.start()


if __name__ == "__main__":
    interview()
