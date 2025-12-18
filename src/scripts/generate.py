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
