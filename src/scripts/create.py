"""
A script for creating new agents.
It requires:
    - agent_type: either "client" or "therapist"
    - agent_name: the name of the new agent to be created
It creates:
- The agent implementation at `src/agents/{agent_type}s/{agent_name}.py`.
- The configuration file at `configs/{agent_type}s/{agent_name}.yaml`.
- A prompt template file at `data/prompts/{agent_type}s/{agent_name}.yaml`.
It also adds the new agent to the corresponding `__init__.py` file.
The configurations for the new agent are specified in the `configs/create.yaml` file.
"""

import os
import hydra
from omegaconf import DictConfig
from src.utils import load_prompts


class FileCreator:
    def __init__(self, configs: DictConfig):
        self.agent_type = configs.agent_type
        self.agent_name = configs.agent_name
        self.agent_class_name = self.get_class_name()
        # Load boilderplate for files
        self.prompts = load_prompts(role="generator", agent_type="files")
        # Define paths
        self.paths = {
            "_init_": f"src/agents/{self.agent_type}s/__init__.py",
            "agent": f"src/agents/{self.agent_type}s/{self.agent_name}.py",
            "config": f"src/configs/{self.agent_type}/{self.agent_name}.yaml",
            "prompt": f"data/prompts/{self.agent_type}/{self.agent_name}.yaml",
        }

    def get_class_name(self) -> str:
        name = self.agent_name + self.agent_type.capitalize()
        return name[0].upper() + name[1:]

    # Create agent implementation file
    def create_agent_file(self) -> None:
        if not os.path.exists(self.paths["agent"]):
            agent_content = self.prompts["agent"].render(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                class_name=self.agent_class_name,
                other_agent_type=(
                    "therapist" if self.agent_type == "client" else "client"
                ),
            )
            with open(self.paths["agent"], "w", encoding="utf-8") as f:
                f.write(agent_content)
            print(
                f"> Created {self.agent_type} agent implementation at: {self.paths['agent']}"
            )
            self.add_to_init()
        else:
            print(
                f"> {self.agent_type} agent implementation already exists at: {self.paths['agent']}"
            )

    # Add implementation to __init__.py:
    def add_to_init(self) -> None:
        prev_line = ""
        is_imported = False
        lines = open(self.paths["_init_"], "r", encoding="utf-8").readlines()
        with open(self.paths["_init_"], "w", encoding="utf-8") as f:
            for line in lines:
                if not is_imported:
                    if prev_line.startswith("from .") and line.strip() == "":
                        f.write(
                            f"from .{self.agent_name} import {self.agent_class_name}\n"
                        )
                        is_imported = True
                elif line.strip() == "}":
                    f.write(f'    "{self.agent_name}": {self.agent_class_name},\n')
                elif line.strip() == "]":
                    f.write(f'    "{self.agent_class_name}",\n')
                f.write(line)
                prev_line = line
        print(f"> Updated {self.paths['_init_']} to include {self.agent_class_name}.")

    # Create configuration file
    def create_config_file(self) -> None:
        if not os.path.exists(self.paths["config"]):
            config_content = self.prompts["config"].render(
                agent_name=self.agent_name, agent_type=self.agent_type
            )
            with open(self.paths["config"], "w", encoding="utf-8") as f:
                f.write(config_content)
            print(
                f"> Created {self.agent_type} configuration at: {self.paths['config']}"
            )
        else:
            print(
                f"> {self.agent_type} configuration already exists at: {self.paths['config']}"
            )

    # Create prompt template file
    def create_prompt_file(self) -> None:
        if not os.path.exists(self.paths["prompt"]):
            prompt_content = self.prompts["prompt"].render()
            with open(self.paths["prompt"], "w", encoding="utf-8") as f:
                f.write(prompt_content)
            print(
                f"> Created {self.agent_type} prompt template at: {self.paths['prompt']}"
            )
        else:
            print(
                f"> {self.agent_type} prompt template already exists at: {self.paths['prompt']}"
            )

    def create_files(self) -> None:
        self.create_agent_file()
        self.create_config_file()
        self.create_prompt_file()
        print("> File creation process completed.")


@hydra.main(version_base=None, config_path="../configs", config_name="create")
def main(configs: DictConfig) -> None:
    file_creator = FileCreator(configs=configs)
    if configs.agent_type not in ["client", "therapist"]:
        raise ValueError("agent_type must be either 'client' or 'therapist'")
    file_creator.create_files()


if __name__ == "__main__":
    main()
