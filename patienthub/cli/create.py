# coding=utf-8
# Licensed under the MIT License;

"""
A script for creating new agents.
It requires:
    - agent_type: either "client" or "therapist"
    - agent_name: the name of the new agent to be created
It creates:
    - The agent implementation at `patienthub/{agent_type}s/{agent_name}.py`
    - A prompt template file at `data/prompts/{agent_type}/{agent_name}.yaml`
It also registers the new agent in the corresponding `__init__.py` file.

Usage:
    # Create a new client agent
    patienthub create agent_type=client agent_name=myClient

    # Create a new therapist agent
    patienthub create agent_type=therapist agent_name=myTherapist
"""

import os
import re
import hydra
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.utils import load_prompts
from patienthub.utils.logger import console


@dataclass
class CreateConfig:
    """Configuration for creating new agents."""

    agent_type: str = ""
    agent_name: str = "myAgent"
    prompt_path: str = "data/prompts/cli/create.yaml"


cs = ConfigStore.instance()
cs.store(name="create", node=CreateConfig)


class AgentCreator:
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.agent_name = configs.agent_name
        self.agent_type = configs.agent_type
        self.agent_class_name = self.get_class_name()
        self.prompts = load_prompts(configs.prompt_path)
        self.paths = {
            "init": f"patienthub/{self.agent_type}s/__init__.py",
            "agent": f"patienthub/{self.agent_type}s/{self.agent_name}.py",
            "prompt": f"data/prompts/{self.agent_type}/{self.agent_name}.yaml",
        }
        if self.agent_type == "client":
            self.paths["schema"] = f"patienthub/schemas/{self.agent_name}.py"
            self.paths["schema_init"] = "patienthub/schemas/__init__.py"

    def get_class_name(self) -> str:
        name = self.agent_name + self.agent_type.capitalize()
        return name[0].upper() + name[1:]

    @staticmethod
    def sub_once(content: str, pattern: str, repl: str, description: str) -> str:
        """Apply a single substitution, raising if the pattern is not found."""
        new_content, n = re.subn(pattern, repl, content, count=1)
        if n == 0:
            raise ValueError(
                f"Failed to update {description}: pattern '{pattern}' not found."
            )
        return new_content

    def create_agent(self) -> None:
        agent_path = self.paths["agent"]
        if os.path.exists(agent_path):
            console.print(
                f"[yellow]Warning: Agent file already exists at: {agent_path}[/yellow]"
            )
            return

        agent_content = self.prompts["agent"].render(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            class_name=self.agent_class_name,
        )
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(agent_content)

        console.print(f"> Created new agent at: [cyan]{agent_path}[/cyan]")

    def register_in_init(
        self,
        init_path: str,
        import_line: str,
        label: str,
        dict_entries: list[tuple[str, str]] = (),
        list_entries: list[tuple[str, str]] = (),
    ) -> None:
        """Add an import plus registry/list entries to an ``__init__.py``."""
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        if import_line in content:
            console.print(
                f"[yellow]Warning: {init_path} already contains {label}.[/yellow]"
            )
            return

        content = self.sub_once(
            content,
            r"(from \.\w+ import [^\n]+\n)(?!\s*from \.)",
            rf"\1{import_line}\n",
            f"imports in {init_path}",
        )
        for name, entry in dict_entries:
            content = self.sub_once(
                content,
                rf"({name}\s*=\s*\{{[^}}]*)(}})",
                rf"\1{entry}\n\2",
                f"{name} in {init_path}",
            )
        for name, entry in list_entries:
            content = self.sub_once(
                content,
                rf"({name}\s*=\s*\[[^\]]*?)(\])",
                rf"\1{entry}\n\2",
                f"{name} in {init_path}",
            )

        with open(init_path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(
            f"> Updated [cyan]{init_path}[/cyan] to include [cyan]{label}[/cyan]."
        )

    def update_init(self) -> None:
        """Register the agent's import, class, and config in the package __init__.py."""
        name = self.agent_name
        class_name = self.agent_class_name
        registry = f"{self.agent_type.upper()}_REGISTRY"
        config_registry = f"{self.agent_type.upper()}_CONFIG_REGISTRY"
        self.register_in_init(
            self.paths["init"],
            import_line=f"from .{name} import {class_name}, {class_name}Config",
            label=class_name,
            dict_entries=[
                (registry, f'    "{name}": {class_name},'),
                (config_registry, f'    "{name}": {class_name}Config,'),
            ],
        )

    def create_schema(self) -> None:
        schema_path = self.paths["schema"]
        if os.path.exists(schema_path):
            console.print(
                f"[yellow]Warning: Schema file already exists at: {schema_path}[/yellow]"
            )
            return
        schema_content = self.prompts["schema"].render(class_name=self.agent_class_name)
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write(schema_content)
        console.print(f"> Created schema at: [cyan]{schema_path}[/cyan]")

    def update_schema_init(self) -> None:
        """Register the new schema in patienthub/schemas/__init__.py."""
        name = self.agent_name
        schema_class = f"{self.agent_class_name}Character"
        self.register_in_init(
            self.paths["schema_init"],
            import_line=f"from .{name} import {schema_class}",
            label=schema_class,
            dict_entries=[
                ("CLIENT_SCHEMA_REGISTRY", f'    "{name}": {schema_class},'),
            ],
            list_entries=[
                ("__all__", f'    "{schema_class}",'),
            ],
        )

    def create_prompt(self) -> None:
        prompt_path = self.paths["prompt"]
        if os.path.exists(prompt_path):
            console.print(
                f"[yellow]Warning: Prompt template already exists at: {prompt_path}[/yellow]"
            )
            return
        prompt_content = self.prompts["prompt"].render()
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_content)
        console.print(f"> Created prompt template at: [cyan]{prompt_path}[/cyan]")

    def create_files(self) -> None:
        if self.agent_type not in ("client", "therapist"):
            raise ValueError(
                "We currently only support generating files for 'client' or 'therapist' agents."
            )

        # Each step is independently idempotent, so a partially-completed run
        # can be finished by simply re-running the command.
        self.create_agent()
        self.update_init()
        if self.agent_type == "client":
            self.create_schema()
            self.update_schema_init()
        self.create_prompt()
        console.print("> File creation completed.")


@hydra.main(version_base=None, config_name="create")
def create(configs: DictConfig) -> None:
    agent_type = configs.agent_type
    if not agent_type or agent_type not in ("client", "therapist"):
        raise ValueError("agent_type is required (either 'client' or 'therapist').")
    agent_creator = AgentCreator(configs)
    agent_creator.create_files()


if __name__ == "__main__":
    create()
