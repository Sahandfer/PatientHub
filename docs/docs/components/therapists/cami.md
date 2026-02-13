# CAMI

The CAMI therapist is an LLM-based counselor agent that follows a Motivational Interviewing (MI) workflow, using prompt templates and a topic graph to steer the conversation.

## Overview

| Property  | Value                                 |
| --------- | ------------------------------------- |
| **Key**   | `cami`                                |
| **Type**  | LLM-based                             |
| **Focus** | Motivational Interviewing (MI) + topics |

## How It Works (High Level)

- Loads prompts from `data/prompts/therapist/cami.yaml`
- Loads a topic graph from `data/resources/CAMI/topic_graph.json` (configurable)
- On each turn, uses the LLM to:
  - infer the client stage (`Precontemplation`, `Contemplation`, `Preparation`)
  - choose up to 2 MI strategies
  - choose the next topic (using a topic stack and the topic graph)
  - generate candidate counselor responses, select one, and optionally refine it

Note: the first `generate_response(...)` call returns a greeting (from the `greeting` prompt).

## Configuration

### YAML Configuration

```yaml
therapist:
  agent_type: cami
  model_type: OPENAI
  model_name: gpt-4o
  topic_graph: data/resources/CAMI/topic_graph.json
  goal: reducing drug use
  behavior: drug use
```

### Python Usage

```python
from omegaconf import OmegaConf

from patienthub.therapists import get_therapist

config = OmegaConf.create(
    {
        "agent_type": "cami",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "topic_graph": "data/resources/CAMI/topic_graph.json",
        "goal": "reducing drug use",
        "behavior": "drug use",
    }
)

therapist = get_therapist(configs=config, lang="en")
```

## Parameters

| Parameter     | Type   | Default                              | Description |
| ------------- | ------ | ------------------------------------ | ----------- |
| `agent_type`  | string | `"cami"`                             | Therapist identifier |
| `model_type`  | string | `"OPENAI"`                           | Model provider key |
| `model_name`  | string | `"gpt-4o"`                           | Model identifier |
| `topic_graph` | string | `data/resources/CAMI/topic_graph.json` | Topic graph JSON path |
| `goal`        | string | `"reducing drug use"`                | Target goal used in prompts |
| `behavior`    | string | `"drug use"`                         | Target behavior used in prompts |
| `temperature` | float  | `0.7`                                | Sampling temperature |
| `max_tokens`  | int    | `8192`                               | Max response tokens |
| `max_retries` | int    | `3`                                  | API retry attempts |
| `lang`        | string | `"en"`                               | Language key for prompt loading |

## Notes

- The CAMI therapist relies on the prompt templates and topic graph; it does not load character/persona JSON files.

## Use Cases

- MI-style counseling simulations with topic guidance
- Training/evaluation where topic coverage and strategy adherence matter
