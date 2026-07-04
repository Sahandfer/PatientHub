---
sidebar_position: 2
---

# Adding New Evaluators

This guide explains how to add new evaluation methods to PatientHub.

## Overview

Evaluators assess the quality of simulations and generated artifacts using an LLM as a judge. Every evaluator subclasses `LLMJudge`, is keyed by an `agent_name`, and reads its scoring schema (the `dimensions`) from a prompt YAML. PatientHub currently ships two evaluators:

- `conv_judge`: evaluates a therapy session (conversation).
- `profile_judge`: evaluates a generated client profile.

Adding a new evaluator means writing a small subclass plus a config dataclass, registering both, and providing a prompt YAML.

## Architecture

```
patienthub/evaluators/
├── __init__.py       # Registries and get_evaluator()
├── base.py           # LLMJudge, LLMJudgeConfig
├── conv.py           # ConvJudge, ConvJudgeConfig
├── profile.py        # ProfileJudge, ProfileJudgeConfig
└── your_evaluator.py # Your new evaluator
```

`base.py` does the heavy lifting: it loads the prompt from `prompt_path`, builds Pydantic response models from the `dimensions` in that YAML, calls the chat model with `response_format=<dimension model>`, and returns one structured result per dimension. Each evaluator subclass typically just prepares the `data` payload and calls `self.evaluate_dimensions(data)`.

The base config `LLMJudgeConfig` subclasses `APIModelConfig`, so every evaluator config inherits these fields:

| Field           | Default  | Notes                                 |
| --------------- | -------- | ------------------------------------- |
| `model_type`    | `OPENAI` | Chat model backend                    |
| `model_name`    | `gpt-4o` | Model identifier                      |
| `temperature`   | `0.7`    |                                       |
| `max_tokens`    | `8192`   |                                       |
| `max_retries`   | `3`      |                                       |
| `lang`          | `en`     | Prompt language                       |
| `use_reasoning` | `False`  | Adds a `reasoning` field per judgment |

## Step 1: Create Evaluator File

Create a new file in `patienthub/evaluators/`. Define a config dataclass (subclassing `LLMJudgeConfig`) and an evaluator class (subclassing `LLMJudge`) that implements `evaluate`:

```python
# patienthub/evaluators/myEvaluator.py

from typing import Any, Dict
from omegaconf import DictConfig
from dataclasses import dataclass

from .base import LLMJudge, LLMJudgeConfig


@dataclass
class MyEvaluatorConfig(LLMJudgeConfig):
    agent_name: str = "my_evaluator"
    prompt_path: str = "data/prompts/evaluator/my_evaluator.yaml"


class MyEvaluator(LLMJudge):
    """Your custom evaluation method.

    Describe what this evaluator measures and what input it expects.
    """

    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def evaluate(self, data: Dict[str, Any], *args) -> Dict[str, Any]:
        # Validate/prepare the payload your prompt expects.
        if not data:
            print("No data provided for evaluation.")
            return {}

        # The base class renders the prompt with this `data` (as `{{data.*}}`),
        # calls the model per dimension, and returns structured results.
        return self.evaluate_dimensions(data)
```

The base class references `data` inside the prompt's Jinja2 template (e.g. `{{data.profile}}` or `{{data.conv_history}}`), so shape the `data` dict to match the fields your prompt uses.

## Step 2: Register the Evaluator

Add your evaluator and its config to the registries in `patienthub/evaluators/__init__.py`:

```python
# patienthub/evaluators/__init__.py
from .myEvaluator import MyEvaluator, MyEvaluatorConfig

EVALUATOR_REGISTRY = {
    "conv_judge": ConvJudge,
    "profile_judge": ProfileJudge,
    "my_evaluator": MyEvaluator,
}

EVALUATOR_CONFIG_REGISTRY = {
    "conv_judge": ConvJudgeConfig,
    "profile_judge": ProfileJudgeConfig,
    "my_evaluator": MyEvaluatorConfig,
}
```

`get_evaluator(agent_name, configs=None, lang="en")` looks the evaluator up by `agent_name`. Registering the config lets `get_evaluator` construct sensible defaults when `configs` is not passed, and lets the config be selected as a Hydra group (`evaluator=my_evaluator`).

## Step 3: Define Evaluation Dimensions

Dimensions are **not** Python objects — they live in the prompt YAML referenced by `prompt_path`. Create it with a `sys_prompt` (Jinja2 template) and a `dimensions` list. Each dimension has a `name`, a `description`, and either a scoring `paradigm` or a list of `aspects` that inherit the dimension's `paradigm` and `range`:

```yaml
# data/prompts/evaluator/my_evaluator.yaml
sys_prompt: |
  You are an expert evaluator assessing therapy conversations.

  ## Conversation History:
  {{data.conv_history}}

  Return the judgment in the required structured format.

dimensions:
  - name: empathy
    description: Whether the therapist demonstrates understanding of the client's emotional experience.
    paradigm: scalar
    range: [1, 5]
  - name: authenticity
    description: How realistic and consistent the simulated client's responses are.
    paradigm: scalar
    range: [1, 5]
    aspects:
      - name: profile_match
        description: Responses match the character profile
      - name: consistency
        description: Maintains a consistent personality
```

Supported paradigms and their returned fields:

| Paradigm      | Returned Field        | Example                         |
| ------------- | --------------------- | ------------------------------- |
| `binary`      | `label: bool`         | `{"label": true}`               |
| `scalar`      | `score: int`          | `{"score": 4}`                  |
| `categorical` | `label: Literal[...]` | `{"label": "very consistent"}`  |
| `extraction`  | `snippets: List[str]` | `{"snippets": ["Client: ..."]}` |

If `use_reasoning=True`, each judged item also gets a `reasoning` field. Dimensions whose `paradigm` is unsupported are skipped when the schema is built.

## Step 4: Create Configuration

You can select and override the evaluator from Hydra using its real config fields. There is a config group per registered evaluator:

```bash
patienthub evaluate \
  evaluator=my_evaluator \
  evaluator.prompt_path=data/prompts/evaluator/my_evaluator.yaml \
  evaluator.use_reasoning=true \
  evaluator.model_name=gpt-4o
```

Overrides must use fields that actually exist on the config (the inherited `APIModelConfig`/`LLMJudgeConfig` fields plus any you add). For `conv_judge`, `evaluator.granularity=turn` selects the granularity.

## Step 5: Test Your Evaluator

Load the evaluator with `get_evaluator` (note that `agent_name` is a required positional argument) and run it on a sample payload:

```python
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator

configs = OmegaConf.create({
    "agent_name": "my_evaluator",
    "prompt_path": "data/prompts/evaluator/my_evaluator.yaml",
    "use_reasoning": False,
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
})

evaluator = get_evaluator(agent_name="my_evaluator", configs=configs, lang="en")

sample = {
    "messages": [
        {"role": "therapist", "content": "How are you feeling today?"},
        {"role": "client", "content": "I've been really anxious lately."},
    ],
}

results = evaluator.evaluate(sample)
print(results)
```

To use the registered defaults instead, call `get_evaluator(agent_name="my_evaluator", lang="en")` without a `configs` argument.

## Checklist

Before submitting your new evaluator:

- [ ] Evaluator class subclassing `LLMJudge` in `patienthub/evaluators/`
- [ ] Config dataclass subclassing `LLMJudgeConfig` with an `agent_name` and `prompt_path`
- [ ] Both registered in `EVALUATOR_REGISTRY` and `EVALUATOR_CONFIG_REGISTRY`
- [ ] Prompt YAML with `sys_prompt` and `dimensions`
- [ ] Verified end-to-end: `patienthub evaluate evaluator=my_evaluator`
- [ ] Documentation updated

## See Also

- [Evaluators Overview](../components/evaluators/overview.md)
- [Evaluation Guide](../guide/evaluation.md)
