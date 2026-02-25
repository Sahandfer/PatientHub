# CBT Therapist

The CBT (Cognitive Behavioral Therapy) therapist implements evidence-based CBT techniques for therapeutic interventions.

## Description

The CBT Therapist is an AI-powered therapeutic agent that employs evidence-based Cognitive Behavioral Therapy techniques. It is designed to help clients identify and challenge negative thought patterns, develop coping strategies, and understand the connection between thoughts, feelings, and behaviors.

## Key Techniques

- **Cognitive restructuring** - Identifying and challenging negative thought patterns
- **Behavioral activation** - Encouraging engagement in positive activities
- **Problem-solving** - Helping clients develop coping strategies
- **Psychoeducation** - Explaining the connection between thoughts, feelings, and behaviors

## Configuration

### YAML Configuration

```yaml
therapist:
  agent_type: CBT
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
        "agent_type": "CBT",
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

| Parameter     | Type   | Default                           | Description                  |
| ------------- | ------ | --------------------------------- | ---------------------------- |
| `prompt_path` | string | `data/prompts/therapist/CBT.yaml` | Path to prompt file          |
| `model_type`  | string | `"OPENAI"`                        | Model provider key           |
| `model_name`  | string | `"gpt-4o"`                        | The LLM model to use         |
| `temperature` | float  | `0.7`                             | Controls response randomness |

## Use Cases

- CBT training simulations
- Research on therapeutic techniques
- Educational demonstrations of CBT principles
