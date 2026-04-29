# Cami

> A Counselor Agent for Motivational Interviewing through State Inference and Topic Exploration

## Overview

| Property  | Value                                   |
| --------- | --------------------------------------- |
| **Key**   | `cami`                                  |
| **Type**  | LLM-based                               |
| **Focus** | Motivational Interviewing (MI) + topics |

## Key Features

- **Stage inference**: Infers the client's readiness stage (`Precontemplation`, `Contemplation`, `Preparation`) each turn
- **MI strategies**: Selects up to 2 MI-aligned strategies per response
- **Topic graph navigation**: Explores counseling topics using a configurable topic graph and topic stack
- **Multi-candidate generation**: Generates several candidate responses and selects the best one

## How It Works

1. **Init**: Loads prompts from `data/prompts/therapist/cami.yaml` and a topic graph from JSON.
2. **Greeting**: The first `generate_response()` call returns a greeting (from the `greeting` prompt key).
3. **Each turn**:
   - Infers client stage from conversation history
   - Selects MI strategies
   - Picks the next topic using the topic stack and graph
   - Generates candidate responses, selects and optionally refines one

## Usage

### CLI

```bash
patienthub simulate therapist=cami
```

### Python

```python
from patienthub.therapists import get_therapist

therapist = get_therapist(agent_name="cami", lang='en')

response = therapist.generate_response("I don't really want to talk about this.")
print(response.content)
```

## Configuration

| Parameter     | Type   | Default                                | Description                     |
| ------------- | ------ | -------------------------------------- | ------------------------------- |
| `agent_name`  | string | `"cami"`                               | Therapist identifier            |
| `prompt_path` | string | `data/prompts/therapist/cami.yaml`     | Path to prompt file             |
| `topic_graph` | string | `data/resources/CAMI/topic_graph.json` | Topic graph JSON path           |
| `goal`        | string | `"reducing drug use"`                  | Target goal used in prompts     |
| `behavior`    | string | `"drug use"`                           | Target behavior used in prompts |
| `model_type`  | string | `"OPENAI"`                             | Model provider key              |
| `model_name`  | string | `"gpt-4o"`                             | Model identifier                |
| `temperature` | float  | `0.7`                                  | Sampling temperature            |
| `max_tokens`  | int    | `8192`                                 | Max response tokens             |
| `max_retries` | int    | `3`                                    | API retry attempts              |
| `lang`        | string | `"en"`                                 | Language key for prompt loading |

## Notes

- Cami relies on prompt templates and a topic graph; it does not load character/persona JSON files.
- The topic graph defines the counseling topics and their relationships.

## Use Cases

- MI-style counseling simulations with topic guidance
- Training/evaluation where topic coverage and MI strategy adherence matter
