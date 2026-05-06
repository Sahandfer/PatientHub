import logging
from .therapySession import TherapySession, TherapySessionConfig

from omegaconf import DictConfig

logger = logging.getLogger(__name__)

EVENT_REGISTRY = {
    "therapy_session": TherapySession,
}
EVENT_CONFIG_REGISTRY = {
    "therapy_session": TherapySessionConfig,
}


def get_event(event_name: str, configs: DictConfig = None):
    if event_name not in EVENT_REGISTRY:
        raise ValueError(f"Unknown event type: {event_name}")
    if configs is None:
        configs = get_event_config(event_name)
    try:
        event = EVENT_REGISTRY[event_name](configs=configs)
    except Exception as e:
        logger.error("Failed to initialize event '%s': %s", event_name, e, exc_info=True)
        raise ValueError(f"Error initializing event '{event_name}'") from e
    logger.info(
        "Loaded event '%s' -> %s",
        event_name,
        ", ".join(f"{k}={v}" for k, v in vars(configs).items()),
    )
    return event


def get_event_config(event_name: str):
    if event_name in EVENT_CONFIG_REGISTRY:
        return EVENT_CONFIG_REGISTRY[event_name]()
    else:
        raise ValueError(f"Event config for {event_name} not found in registry.")


def register_event_configs(cs):
    for name, config_cls in EVENT_CONFIG_REGISTRY.items():
        cs.store(group="event_configs", name=name, node=config_cls)


__all__ = ["TherapySession", "get_event", "get_event_config"]
