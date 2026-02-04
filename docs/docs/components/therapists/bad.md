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
  key: bad
  config:
    model: gpt-4o
```

### Python Usage

```python
from patienthub.therapists import TherapistRegistry

therapist = TherapistRegistry.create("bad", config={
    "model": "gpt-4o"
})
```

## Parameters

| Parameter | Type   | Default  | Description          |
| --------- | ------ | -------- | -------------------- |
| `model`   | string | `gpt-4o` | The LLM model to use |

## Use Cases

- Training mental health professionals to recognize bad practices
- Testing client agent robustness to poor therapy
- Research on therapeutic alliance and rupture-repair
- Educational demonstrations of what NOT to do

## ⚠️ Important Note

This therapist is intended **only for research and training purposes**. It should never be used in real therapeutic contexts or with actual patients.
