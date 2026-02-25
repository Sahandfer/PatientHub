# Psyche

Psyche is an LLM-based psychiatrist interview therapist driven by a single system prompt template.

## Overview

| Property  | Value                             |
| --------- | --------------------------------- |
| **Key**   | `psyche`                          |
| **Type**  | LLM-based                         |
| **Focus** | Structured intake-style interview |

## How It Works

- Loads prompts from `data/prompts/therapist/psyche.yaml` (`sys_prompt`)
- Initializes the conversation with that system prompt
- Each `generate_response(...)` call appends the latest user message and asks the model for the next assistant message

## Configuration

### YAML Configuration

```yaml
therapist:
  agent_type: psyche
  model_type: OPENAI
  model_name: gpt-4o
  temperature: 0.7
```

### Python Usage

```python
from omegaconf import OmegaConf

from patienthub.therapists import get_therapist

config = OmegaConf.create(
    {
        "agent_type": "psyche",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 8192,
        "max_retries": 3,
    }
)

therapist = get_therapist(configs=config, lang="en")
```

## Parameters

| Parameter     | Type   | Default                              | Description                     |
| ------------- | ------ | ------------------------------------ | ------------------------------- |
| `agent_type`  | string | `"psyche"`                           | Therapist identifier            |
| `prompt_path` | string | `data/prompts/therapist/psyche.yaml` | Path to prompt file             |
| `model_type`  | string | `"OPENAI"`                           | Model provider key              |
| `model_name`  | string | `"gpt-4o"`                           | Model identifier                |
| `temperature` | float  | `0.7`                                | Sampling temperature            |
| `max_tokens`  | int    | `8192`                               | Max response tokens             |
| `max_retries` | int    | `3`                                  | API retry attempts              |
| `lang`        | string | `"en"`                               | Language key for prompt loading |

## Use Cases

- Intake-style interview simulations (psychiatrist role)
- Simple prompt-driven therapist baseline
