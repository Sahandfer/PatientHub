# Psyche

Psyche is an LLM-based psychiatrist agent driven by a structured system prompt, designed for intake-style clinical interviews.

## Overview

| Property  | Value                             |
| --------- | --------------------------------- |
| **Key**   | `psyche`                          |
| **Type**  | LLM-based                         |
| **Focus** | Structured intake-style interview |

## How It Works

1. **Prompt Loading**: Loads a system prompt from `data/prompts/therapist/psyche.yaml`.
2. **Session Init**: Initializes the conversation with that system prompt.
3. **Response Generation**: Each `generate_response()` call appends the client message and asks the model for the next reply.

## Usage

### CLI

```bash
patienthub simulate therapist=psyche
```

### Python

```python
from patienthub.therapists import get_therapist

therapist = get_therapist(agent_name="psyche", lang='en')

response = therapist.generate_response("I've been struggling with sleep and low mood.")
print(response.content)
```

## Configuration

| Parameter     | Type   | Default                              | Description                     |
| ------------- | ------ | ------------------------------------ | ------------------------------- |
| `agent_name`  | string | `"psyche"`                           | Therapist identifier            |
| `prompt_path` | string | `data/prompts/therapist/psyche.yaml` | Path to prompt file             |
| `model_type`  | string | `"OPENAI"`                           | Model provider key              |
| `model_name`  | string | `"gpt-4o"`                           | Model identifier                |
| `temperature` | float  | `0.7`                                | Sampling temperature            |
| `max_tokens`  | int    | `8192`                               | Max response tokens             |
| `max_retries` | int    | `3`                                  | API retry attempts              |
| `lang`        | string | `"en"`                               | Language key for prompt loading |

## Use Cases

- Intake-style interview simulations (psychiatrist role)
- Prompt-driven therapist baseline
- Evaluating client agents in a clinical assessment context
