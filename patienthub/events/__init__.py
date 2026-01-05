from .therapySession import TherapySession, TherapySessionConfig

from omegaconf import DictConfig

EVENT_REGISTRY = {
    "therapySession": TherapySession,
}
EVENT_CONFIG_REGISTRY = {
    "therapySession": TherapySessionConfig,
}


def get_event(configs: DictConfig):
    event_type = configs.event_type
    print(f"Loading {event_type} event...")
    if event_type in EVENT_REGISTRY:
        return EVENT_REGISTRY[event_type](configs=configs)
    else:
        raise ValueError(f"Unknown event type: {event_type}")


def register_event_configs(cs):
    for name, config_cls in EVENT_CONFIG_REGISTRY.items():
        cs.store(group="event", name=name, node=config_cls)


__all__ = ["TherapySession"]
