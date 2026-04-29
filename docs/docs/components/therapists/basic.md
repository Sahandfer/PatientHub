# Basic

A prompt-driven therapist with optional chain-of-thought reasoning, configurable for different therapeutic approaches.

## Overview

| Property  | Value                            |
| --------- | -------------------------------- |
| **Key**   | `basic`                          |
| **Type**  | LLM-based                        |
| **Focus** | Configurable via prompt template |

## Key Features

- **Prompt-driven**: Therapeutic approach is defined entirely by the prompt template
- **Chain-of-thought (CoT)**: Optional reasoning step before generating a response
- **Configurable**: Swap prompt files to target different therapeutic modalities (CBT, MI, etc.)

## How It Works

1. **Prompt Loading**: Loads a system prompt from the configured `prompt_path`.
2. **Session Init**: Builds the conversation with the system prompt as the first message.
3. **Response Generation**: On each turn, appends the user message, calls the LLM, and appends the assistant reply to history.
4. **CoT Mode** (optional): When `use_cot=True`, the model returns structured reasoning alongside the response content.

## Usage

### CLI

```bash
patienthub simulate therapist=basic
```

### Python

```python
from patienthub.therapists import get_therapist

therapist = get_therapist(agent_name="basic", lang='en')

response = therapist.generate_response("Hello, I've been feeling anxious lately.")
print(response.content)
```

## Configuration

| Option        | Type   | Default                           | Description                               |
| ------------- | ------ | --------------------------------- | ----------------------------------------- |
| `prompt_path` | string | `data/prompts/therapist/CBT.yaml` | Path to prompt file                       |
| `use_cot`     | bool   | `False`                           | Enable chain-of-thought structured output |
| `model_type`  | string | `"OPENAI"`                        | Model provider key                        |
| `model_name`  | string | `"gpt-4o"`                        | The LLM model to use                      |
| `temperature` | float  | `0.7`                             | Controls response randomness              |
| `max_tokens`  | int    | `8192`                            | Max response tokens                       |
| `max_retries` | int    | `3`                               | API retry attempts                        |

## Response Format

Without CoT, returns a plain string response. With `use_cot=True`, returns a structured object:

```python
class ResponseWithCOT(BaseModel):
    reasoning: str  # Internal chain-of-thought (not shown to client)
    content: str    # Therapist's actual response
```

## Use Cases

- General-purpose therapist baseline
- CBT training simulations (default prompt)
- Research on different therapeutic prompt designs
- Educational demonstrations
