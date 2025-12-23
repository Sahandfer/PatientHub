from hydra.core.config_store import ConfigStore


def register_configs(config_name: str, config_class):
    from patienthub.clients import register_client_configs
    from patienthub.therapists import register_therapist_configs
    from patienthub.evaluators import register_evaluator_configs
    from patienthub.generators import register_generator_configs

    cs = ConfigStore.instance()
    cs.store(name=config_name, node=config_class)

    # Register configs
    register_client_configs(cs)
    register_therapist_configs(cs)
    register_evaluator_configs(cs)
    register_generator_configs(cs)
