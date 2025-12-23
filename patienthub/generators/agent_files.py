import os
from dataclasses import dataclass
from omegaconf import DictConfig

from patienthub.utils import load_prompts


@dataclass
class AgentFilesGeneratorConfig:
    """Configuration for AgentFiles generator."""

    agent_type: str = "agent_files"


class AgentFilesGenerator:
    def __init__(self, configs: DictConfig):
        self.agent_type = configs.gen_agent_type
        self.agent_name = configs.gen_agent_name
        self.agent_class_name = self.get_class_name()
        # Load boilderplate for files
        self.prompts = load_prompts(role="generator", agent_type="files")
        # Define paths
        self.paths = {
            "_init_": f"patienthub/{self.agent_type}s/__init__.py",
            "agent": f"patienthub/{self.agent_type}s/{self.agent_name}.py",
            "prompt": f"data/prompts/{self.agent_type}/{self.agent_name}.yaml",
        }

    def get_class_name(self) -> str:
        name = self.agent_name + self.agent_type.capitalize()
        return name[0].upper() + name[1:]

    # Create agent implementation file
    def generate_agent_file(self) -> None:
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
    def add_to_import(self, prev_line, current_line) -> str:
        import_str = f"from .{self.agent_name} import {self.agent_class_name}, {self.agent_class_name}Config\n"
        if prev_line.startswith("from .") and current_line.strip() == "":
            return import_str + "\n" + current_line, True
        else:
            return current_line, False

    def add_to_registry(self, prev_line, current_line) -> str:
        client_str = f'    "{self.agent_name}": {self.agent_class_name},\n'
        client_cfg_str = f'    "{self.agent_name}": {self.agent_class_name}Config,\n'

        if current_line.strip() == "}":
            if "Config" in prev_line.strip():
                return client_cfg_str + current_line
            else:
                return client_str + current_line
        else:
            return current_line

    def add_to_init(self) -> None:
        prev_line = ""
        imported_client = False
        lines = open(self.paths["_init_"], "r", encoding="utf-8").readlines()
        with open(self.paths["_init_"], "w", encoding="utf-8") as f:
            for line in lines:
                if not imported_client:
                    line, imported_client = self.add_to_import(prev_line, line)
                else:
                    line = self.add_to_registry(prev_line, line)

                f.write(line)
                prev_line = line
        print(f"> Updated {self.paths['_init_']} to include {self.agent_class_name}.")

    # Create prompt template file
    def generate_prompt_file(self) -> None:
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

    def generate_files(self) -> None:
        self.generate_agent_file()
        self.generate_prompt_file()
        print("> File creation process completed.")
