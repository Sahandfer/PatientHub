import hydra
from omegaconf import DictConfig

from src.utils import load_json
from src.agents.generators import StudentClientGenerator


@hydra.main(version_base=None, config_path="../configs", config_name="generate")
def generate_characters(configs: DictConfig):
    character_generator = StudentClientGenerator(configs=configs)

    data = load_json(configs.input_dir)

    for label, topics in data.items():
        print(f"Generating characters for label: {label}")
        for topic in topics:
            print(f"# {topic}")
            character_generator.create_character(label=label, topic=topic)


if __name__ == "__main__":
    generate_characters()
