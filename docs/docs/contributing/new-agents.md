---
sidebar_position: 1
---

# Adding New Agents

This guide explains how to add new client or therapist agents to PatientHub.

## Quickstart: Auto-generate Boilerplate

The `examples.create` script scaffolds the agent file, prompt template, and registration in one command:

```bash
# Create a new client agent
uv run python -m examples.create agent_type=client agent_name=myClient

# Create a new therapist agent
uv run python -m examples.create agent_type=therapist agent_name=myTherapist
```

This generates:

- `patienthub/clients/myClient.py` (or `patienthub/therapists/myTherapist.py`)
- `data/prompts/client/myClient.yaml` (or `data/prompts/therapist/myTherapist.yaml`)
- Adds the import, registry entry, and config registry entry to the corresponding `__init__.py`
- For new clients only: `patienthub/adapters/myClient.py`

The adapter schema file is a blank Pydantic skeleton with a `TODO`, so the new client can participate in cross-client character conversion once you fill in its schema.

The sections below explain each part in detail.

---

## Step 1: Implement the Agent

### Client Agent

```python
# patienthub/clients/myClient.py

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class MyClientConfig(APIModelConfig):
    """Configuration for MyClient agent."""

    agent_name: str = "myClient"
    prompt_path: str = "data/prompts/client/myClient.yaml"
    data_path: str = "data/characters/MyClient.json"
    data_idx: int = 0


class MyClient(BaseClient):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "Client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

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
from patienthub.utils import load_prompts, get_chat_model


@dataclass
class MyTherapistConfig(APIModelConfig):
    """Configuration for MyTherapist agent."""

    agent_name: str = "myTherapist"
    prompt_path: str = "data/prompts/therapist/myTherapist.yaml"


class MyTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

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

For client agents, also register an adapter schema in `patienthub/adapters/__init__.py` and define it in `patienthub/adapters/myClient.py`.

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

## Step 5: Define the Adapter Schema for New Clients

If you created a client with `examples.create`, PatientHub already created `patienthub/adapters/myClient.py` for you. Fill in the character schema there:

```python
from .base import CharacterModel


class MyClientCharacter(CharacterModel):
    # TODO: replace this with the real schema expected by your client
    pass
```

This schema is used by the adapter framework to:

- validate incoming source profiles
- constrain generated target profiles for your client
- keep cross-client conversion compatible with your runtime expectations

---

## Step 6: Add Tests

The existing smoke tests in `patienthub/tests/clients.py` automatically pick up any client registered in `CLIENT_REGISTRY`. Run them with:

```bash
python -m pytest patienthub/tests/clients.py -v
```

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
uv run python -m examples.simulate client=myClient
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
- [ ] Smoke tests pass: `uv run python -m pytest patienthub/tests/clients.py -v`
- [ ] Documentation page added
- [ ] Works end-to-end: `uv run python -m examples.simulate client=myClient`
