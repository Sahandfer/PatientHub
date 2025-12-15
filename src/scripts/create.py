"""
A script for creating new agents. By running this script, it will ask for a {name} and create:
- `src/agents/{agent_type}s/{agent_name}.py`: The agent implementation.
- `configs/{agent_type}s/{agent_name}.yaml`: The configuration file for the agent.
- `data/prompts/{agent_type}s/{agent_name}.yaml`: A prompt template file for the agent.
"""

import os
import argparse
from src.utils import load_prompts


class FileCreator:
    def __init__(self, args):
        self.agent_type = args.agent_type
        self.agent_name = args.agent_name
        self.agent_class_name = (
            f"{args.agent_name.capitalize()}{args.agent_type.capitalize()}"
        )
        # Load boilderplate for files
        self.prompts = load_prompts(role="generator", agent_type="files")
        # Define paths
        self.paths = {
            "_init_": f"src/agents/{self.agent_type}s/__init__.py",
            "agent": f"src/agents/{self.agent_type}s/{self.agent_name}.py",
            "config": f"src/configs/{self.agent_type}/{self.agent_name}.yaml",
            "prompt": f"data/prompts/{self.agent_type}/{self.agent_name}.yaml",
        }

    # Create agent implementation file
    def create_agent_file(self):
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
    def add_to_init(self):
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
                    f.write(f"    '{self.agent_name}': {self.agent_class_name},\n")
                f.write(line)
                prev_line = line
        print(f"> Updated {self.paths['_init_']} to include {self.agent_class_name}.")

    # Create configuration file
    def create_config_file(self):
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
    def create_prompt_file(self):
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

    def create_files(self):
        self.create_agent_file()
        self.create_config_file()
        self.create_prompt_file()


if __name__ == "__main__":
    # client_name = input("Enter the name of the new client: ")
    args = argparse.ArgumentParser()
    # The type can only be client or therapist for now
    args.add_argument(
        "--agent_type",
        type=str,
        required=True,
        help="The type of the new agent",
        choices=["client", "therapist"],
    )
    args.add_argument(
        "--agent_name",
        type=str,
        required=True,
        help="The name of the new agent (lowercase)",
    )
    args = args.parse_args()
    file_creator = FileCreator(args=args)
    file_creator.create_files()
