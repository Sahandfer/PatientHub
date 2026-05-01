---
sidebar_position: 1
---

# Adding New Agents

This guide explains how to add new client or therapist agents to PatientHub.

## Quickstart: Auto-generate Boilerplate

The `examples.create` script scaffolds the agent file, prompt template, and `__init__.py` registration in one command:

```bash
# Create a new client agent
patienthub create agent_type=client agent_name=myClient

# Create a new therapist agent
patienthub create agent_type=therapist agent_name=myTherapist
```

This generates:

- `patienthub/clients/myClient.py` (or `patienthub/therapists/myTherapist.py`)
- `data/prompts/client/myClient.yaml` (or `data/prompts/therapist/myTherapist.yaml`)
- Adds the import, registry entry, and config registry entry to the corresponding `__init__.py`

The sections below explain each part in detail.

---

## Step 1: Implement the Agent

### Client Agent

File ordering convention: **imports → config dataclass → response schemas (if any) → agent class**.

```python
# patienthub/clients/myClient.py

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig


@dataclass
class MyClientConfig(APIModelConfig):
    """Configuration for MyClient agent."""

    agent_name: str = "myClient"
    prompt_path: str = "data/prompts/client/myClient.yaml"
    data_path: str = "data/characters/MyClient.json"
    data_idx: int = 0


class MyClient(BaseClient):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)  # handles data, prompts, chat_model, build_sys_prompt

    def build_sys_prompt(self):
        self.messages = [
            {"role": "system", "content": self.prompts["sys_prompt"].render(data=self.data)}
        ]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        return res

    def reset(self):
        self.build_sys_prompt()
        self.therapist = None
```

### Therapist Agent

The pattern is identical — inherit from `BaseTherapist` instead:

```python
# patienthub/therapists/myTherapist.py

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseTherapist
from patienthub.configs import APIModelConfig


@dataclass
class MyTherapistConfig(APIModelConfig):
    """Configuration for MyTherapist agent."""

    agent_name: str = "myTherapist"
    prompt_path: str = "data/prompts/therapist/myTherapist.yaml"


class MyTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)  # handles prompts, chat_model, build_sys_prompt

    def build_sys_prompt(self):
        self.messages = [
            {"role": "system", "content": self.prompts["sys_prompt"].render()}
        ]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        return res

    def reset(self):
        self.build_sys_prompt()
        self.client = None
```

---

## Step 2: Register the Agent

If you used `examples.create`, this is done automatically. Otherwise, edit `patienthub/clients/__init__.py` (or `therapists/__init__.py`):

```python
from .myClient import MyClient, MyClientConfig

CLIENT_REGISTRY = {
    # ... existing agents ...
    "myClient": MyClient,
}

CLIENT_CONFIG_REGISTRY = {
    # ... existing configs ...
    "myClient": MyClientConfig,
}
```

---

## Step 3: Create the Prompt Template

```yaml
# data/prompts/client/myClient.yaml
en:
  sys_prompt: |
    You are simulating a patient named {{ data.name }}.

    Background: {{ data.background }}

    Respond as this patient would in a therapy session.
zh:
  sys_prompt: |
    <在这里输入提示文本>
```

---

## Step 4: Create Character Data

```json
[
  {
    "name": "Taylor",
    "age": 29,
    "background": "Recently moved to a new city for work and is experiencing social anxiety.",
    "presenting_problem": "Difficulty meeting new people and persistent worry about social judgment."
  }
]
```

---

## Step 4b: Register a Character Schema

Every client with a character data file must have a Pydantic schema registered in `patienthub/schemas/`. This validates data at load time and ensures all fields required by your prompts are present.

```python
# patienthub/schemas/myClient.py

from pydantic import Field
from patienthub.schemas.base import BaseCharacter


class MyClientCharacter(BaseCharacter):
    name: str = Field(...)
    age: int = Field(...)
    background: str = Field(...)
    presenting_problem: str = Field(...)
```

Then register it in `patienthub/schemas/__init__.py`:

```python
from .myClient import MyClientCharacter

CLIENT_SCHEMA_REGISTRY = {
    # ... existing schemas ...
    "myClient": MyClientCharacter,
}
```

:::tip Required fields
All fields referenced in your prompt templates (e.g. `{{ data.background }}`) must be defined in the schema **without** a default value — use `Field(...)`. This ensures a missing field fails at load time rather than silently producing a broken prompt.
:::

---

## Step 5: Add Tests

Two test suites run automatically for any registered client:

**Smoke tests** — verify instantiation, prompts, and messages:

```bash
uv run python -m pytest patienthub/tests/clients.py -v
```

**Schema validation tests** — validate every entry in your character JSON against its registered schema:

```bash
uv run python -m pytest patienthub/tests/schemas.py -v
```

Schema tests also run automatically in CI whenever you push changes to `patienthub/clients/`, `patienthub/schemas/`, or `data/characters/`.

For agent-specific tests:

```python
import pytest
from unittest.mock import patch, MagicMock
from omegaconf import OmegaConf
from patienthub.clients import CLIENT_CONFIG_REGISTRY, CLIENT_REGISTRY


@pytest.fixture
def client():
    mock_model = MagicMock()
    mock_model.generate.return_value = MagicMock(content="mock response")

    with patch("patienthub.utils.models.get_chat_model", return_value=mock_model):
        cfg = OmegaConf.structured(CLIENT_CONFIG_REGISTRY["myClient"])
        return CLIENT_REGISTRY["myClient"](configs=cfg)


def test_instantiation(client):
    assert client is not None


def test_name_is_set(client):
    assert client.name == "Taylor"


def test_generate_response(client):
    response = client.generate_response("How have you been feeling?")
    assert response.content == "mock response"
```

---

## Step 6: Add Documentation

Create a doc page at `docs/docs/components/clients/myagent.md` following the style of existing client docs:

```markdown
# MyClient

> Paper Title (if applicable)

**Venue**: Conference Year (if applicable)

## Overview

Brief description of the method.

## Key Features

- Feature 1
- Feature 2

## Usage

### CLI

\`\`\`bash
patienthub simulate client=myClient
\`\`\`

### Python

\`\`\`python
from patienthub.clients import get_client

client = get_client(agent_name="myClient", lang="en")
response = client.generate_response("How have you been feeling?")
print(response.content)
\`\`\`

## Configuration

| Option       | Type   | Default                             | Description        |
| ------------ | ------ | ----------------------------------- | ------------------ |
| `prompt_path`| string | `data/prompts/client/myClient.yaml` | Path to prompt file |
| `data_path`  | string | `data/characters/MyClient.json`     | Path to character file |
| `data_idx`   | int    | `0`                                 | Character index    |
```

---

## Checklist

Before submitting your new agent:

- [ ] Agent class in `patienthub/clients/` (or `therapists/`)
- [ ] Config dataclass with `agent_name`, `prompt_path`, and any extra fields
- [ ] Registered in `CLIENT_REGISTRY` and `CLIENT_CONFIG_REGISTRY` in `__init__.py`
- [ ] Prompt YAML created at `data/prompts/client/<agent_name>.yaml`
- [ ] Character data file created (if applicable)
- [ ] Pydantic schema created in `patienthub/schemas/` with all prompt fields required
- [ ] Schema registered in `CLIENT_SCHEMA_REGISTRY` in `patienthub/schemas/__init__.py`
- [ ] Smoke tests pass: `uv run python -m pytest patienthub/tests/clients.py -v`
- [ ] Schema tests pass: `uv run python -m pytest patienthub/tests/schemas.py -v`
- [ ] Documentation page added
- [ ] Works end-to-end: `patienthub simulate client=myClient`
