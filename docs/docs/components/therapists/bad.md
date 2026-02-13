# Bad Therapist

The Bad Therapist is intentionally designed to demonstrate poor therapeutic practices, useful for training and research purposes.

## Overview

| Property  | Value                    |
| --------- | ------------------------ |
| **Key**   | `bad`                    |
| **Type**  | LLM-based                |
| **Focus** | Counter-example Training |

## Description

The Bad Therapist agent is deliberately programmed to exhibit poor therapeutic behaviors. This is valuable for training mental health professionals to recognize problematic practices, testing how client agents respond to suboptimal therapy, and researching the impact of poor therapeutic alliance.

## Key Features

- **Poor boundaries** - Demonstrates inappropriate therapeutic boundaries
- **Dismissive responses** - Shows lack of empathy and validation
- **Bad advice** - Provides unhelpful or harmful suggestions
- **Alliance ruptures** - Creates situations that damage therapeutic rapport

## Configuration

### YAML Configuration

```yaml
therapist:
  agent_type: bad
  model_type: OPENAI
  model_name: gpt-4o
  data_path: data/characters/therapists.json
  data_idx: 0
```

### Python Usage

```python
from omegaconf import OmegaConf

from patienthub.therapists import get_therapist

config = OmegaConf.create(
    {
        "agent_type": "bad",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "data_path": "data/characters/therapists.json",
        "data_idx": 0,
    }
)
therapist = get_therapist(configs=config, lang="en")
```

## Parameters

| Parameter    | Type   | Default     | Description                  |
| ------------ | ------ | ----------- | ---------------------------- |
| `model_type` | string | `"OPENAI"`  | Model provider key           |
| `model_name` | string | `"gpt-4o"`  | The LLM model to use         |
| `data_path`  | string | (varies)    | Therapist profile JSON path  |
| `data_idx`   | int    | `0`         | Index into the JSON list     |

## Use Cases

- Training mental health professionals to recognize bad practices
- Testing client agent robustness to poor therapy
- Research on therapeutic alliance and rupture-repair
- Educational demonstrations of what NOT to do

## ⚠️ Important Note

This therapist is intended **only for research and training purposes**. It should never be used in real therapeutic contexts or with actual patients.
