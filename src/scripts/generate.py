"""
An example for generating characters for simulations.
It requires:
    - A generator agent (specified by gen_type in the configuration)
It creates and saves a character based on the specified configurations.
The configurations for the generator are specified in the `configs/generate.yaml` file.
"""

import hydra
from omegaconf import DictConfig
from src.agents.generators import get_generator


def generate_client(configs: DictConfig):
    generator = get_generator(configs=configs)
    generator.generate_character()


@hydra.main(version_base=None, config_path="../configs", config_name="generate")
def generate(configs: DictConfig):
    if configs.gen_type == "client":
        generate_client(configs)
    else:
        print("Generation type is not supported.")


if __name__ == "__main__":
    generate()
