from .therapySession import TherapySession, TherapySessionConfig

from omegaconf import DictConfig

EVENT_REGISTRY = {
    "therapy_session": TherapySession,
}
EVENT_CONFIG_REGISTRY = {
    "therapy_session": TherapySessionConfig,
}


def get_event(event_name: str, configs: DictConfig = None):
    print(f"Loading {event_name} event...")
    if event_name in EVENT_REGISTRY:
        if configs is None:
            configs = get_event_config(event_name)
        return EVENT_REGISTRY[event_name](configs=configs)
    else:
        raise ValueError(f"Unknown event type: {event_name}")


def get_event_config(event_name: str):
    if event_name in EVENT_CONFIG_REGISTRY:
        return EVENT_CONFIG_REGISTRY[event_name]()
    else:
        raise ValueError(f"Event config for {event_name} not found in registry.")


def register_event_configs(cs):
    for name, config_cls in EVENT_CONFIG_REGISTRY.items():
        cs.store(group="event", name=name, node=config_cls)


__all__ = ["TherapySession", "get_event", "get_event_config"]
