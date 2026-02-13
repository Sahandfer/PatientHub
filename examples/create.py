"""
A script for creating new agents.
It requires:
    - agent_type: either "client" or "therapist"
    - agent_name: the name of the new agent to be created
It creates:
- The agent implementation at `patienthub/{agent_type}s/{agent_name}.py`.
- A prompt template file at `data/prompts/{agent_type}/{agent_name}.yaml`.
It also adds the new agent to the corresponding `__init__.py` file.

Usage:
    # Create a new client agent
    uv run python -m examples.create agent_type=client agent_name=myClient

    # Create a new therapist agent
    uv run python -m examples.create agent_type=therapist agent_name=myTherapist
"""

import os
import re
import hydra
from jinja2 import Template
from typing import Any, List
from omegaconf import DictConfig
from dataclasses import dataclass, field
from hydra.core.config_store import ConfigStore

AGENT_TEMPLATE = Template(
    '''\
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import {% if agent_type == "client" %}BaseClient{% else %}BaseTherapist{% endif %}
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

@dataclass
class {{class_name}}Config(APIModelConfig):
    """
    Configuration for the {{class_name}} agent.
    """
    agent_type: str = "{{agent_name}}"
    prompt_path: str = "data/prompts/{{agent_type}}/{{agent_name}}.yaml"
    data_path: str = "data/characters/{{agent_type}}s.json"
    data_idx: int = 0

class {{class_name}}({% if agent_type == "client" %}BaseClient{% else %}BaseTherapist{% endif %}):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "{{class_name}}")

        self.chat_model = get_chat_model(configs)
        # TODO: Define the prompts for the client agent
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    # TODO: Initialize the system prompt
    def build_sys_prompt(self):
        self.messages = [{"role": "system", "content": self.prompts["sys_prompt"].render(data=self.data)}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
'''
)

PROMPT_TEMPLATE = Template(
    """\
en: 
  sys_prompt: |
    <insert prompt text here>
zh: 
  sys_prompt: |
    <在这里输入提示文本>
"""
)


@dataclass
class CreateConfig:
    """Configuration for creating new agents."""

    defaults: List[Any] = field(default_factory=lambda: ["_self_"])
    agent_type: str = "client"
    agent_name: str = "myClient"


cs = ConfigStore.instance()
cs.store(name="create", node=CreateConfig)


class Generator:
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.agent_type = configs.agent_type
        self.agent_name = configs.agent_name
        self.agent_class_name = self.get_class_name()
        self.prompts = {"agent": AGENT_TEMPLATE, "prompt": PROMPT_TEMPLATE}
        self.paths = {
            "init": f"patienthub/{self.agent_type}s/__init__.py",
            "agent": f"patienthub/{self.agent_type}s/{self.agent_name}.py",
            "prompt": f"data/prompts/{self.agent_type}/{self.agent_name}.yaml",
        }

    def get_class_name(self) -> str:
        name = self.agent_name + self.agent_type.capitalize()
        return name[0].upper() + name[1:]

    def create_agent(self) -> None:
        agent_content = self.prompts["agent"].render(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            class_name=self.agent_class_name,
        )
        agent_path = self.paths["agent"]
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(agent_content)

        print(f"> Created new agent at: {agent_path}")

    def update_init(self) -> None:
        """Add import, registry entry, and config registry entry to the corresponding __init__.py."""
        init_path = self.paths["init"]
        name = self.agent_name
        class_name = self.agent_class_name

        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        import_line = f"from .{name} import {class_name}, {class_name}Config"
        if import_line in content:
            print(f"> {init_path} already contains {class_name}.")
            return

        content = re.sub(
            r"(from \.\w+ import [^\n]+\n)(?!\s*from \.)",
            rf"\1{import_line}\n",
            content,
            count=1,
        )

        registry_entry = f'    "{name}": {class_name},'
        content = re.sub(
            r"(_REGISTRY\s*=\s*\{[^}]*)(})",
            rf"\1{registry_entry}\n\2",
            content,
            count=1,
        )

        config_entry = f'    "{name}": {class_name}Config,'
        content = re.sub(
            r"(_CONFIG_REGISTRY\s*=\s*\{[^}]*)(})",
            rf"\1{config_entry}\n\2",
            content,
            count=1,
        )

        with open(init_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"> Updated {init_path} to include {class_name}.")

    def create_prompt(self) -> None:
        prompt_path = self.paths["prompt"]
        prompt_content = self.prompts["prompt"].render()
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_content)
        print(f"> Created prompt template at: {prompt_path}")

    def generate_files(self) -> None:
        if self.agent_type not in ("client", "therapist"):
            raise ValueError(
                "We currently only support generating files for 'client' or 'therapist' agents."
            )

        agent_path = self.paths["agent"]
        if os.path.exists(agent_path):
            print(f"> Agent file already exists at: {agent_path}")
        else:
            self.create_agent()
            self.update_init()
            self.create_prompt()
            print("> File creation process completed.")


@hydra.main(version_base=None, config_name="create")
def main(configs: DictConfig) -> None:
    file_creator = Generator(configs)
    file_creator.generate_files()


if __name__ == "__main__":
    main()
