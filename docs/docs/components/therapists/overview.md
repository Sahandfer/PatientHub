# Therapist Agents API

Therapist agents in PatientHub provide the therapeutic interventions during simulated conversations. They can range from sophisticated AI-powered therapists to simple rule-based systems, enabling various research and training scenarios.

## Available Therapists

| Therapist                 | Key      | Description                                                        |
| ------------------------- | -------- | ------------------------------------------------------------------ |
| [**Cami**](./cami.md)     | `cami`   | MI counselor with stage inference and topic graph exploration      |
| [**Psyche**](./psyche.md) | `psyche` | Psychiatrist agent with structured intake-style interview          |
| [**Basic**](./basic.md)   | `basic`  | Prompt-driven therapist with optional chain-of-thought             |
| [**Eliza**](./eliza.md)   | `eliza`  | Classic pattern-matching therapist based on the original ELIZA     |
| [**User**](./user.md)     | `user`   | Human-in-the-loop therapist for interactive sessions               |

## Listing Available Therapists

```python
from patienthub.therapists import THERAPIST_REGISTRY, THERAPIST_CONFIG_REGISTRY

# List all therapist types
print("Available therapists:", list(THERAPIST_REGISTRY.keys()))

# Get config class for a therapist
config_class = THERAPIST_CONFIG_REGISTRY['basic']
print(config_class)
```

## Loading a Therapist

```python
from patienthub.therapists import get_therapist

therapist = get_therapist(agent_name='basic', lang='en')
```

## Loading a Therapist with Custom Configurations

```python
from omegaconf import OmegaConf
from patienthub.therapists import get_therapist

config = OmegaConf.create(
    {
        "agent_name": "basic",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "prompt_path": "data/prompts/therapist/CBT.yaml",
        "temperature": 0.7,
        "max_tokens": 8192,
        "max_retries": 3,
        "use_cot": False,
    }
)
therapist = get_therapist(agent_name='basic', configs=config, lang='en')
```

## Response Generation

```python
response = therapist.generate_response("Hello, I've been feeling anxious lately.")
print(f"Response: {response.content}")
```

## Data Format

- Prompt data is stored in `data/prompts/therapist`.

## Configuration Options

### Common Options

| Option        | Type  | Default    | Description                                                                          |
| ------------- | ----- | ---------- | ------------------------------------------------------------------------------------ |
| `agent_name`  | str   | required   | Therapist identifier                                                                 |
| `model_type`  | str   | `"OPENAI"` | Model provider key (used to read `${MODEL_TYPE}_API_KEY` / `${MODEL_TYPE}_BASE_URL`) |
| `model_name`  | str   | `"gpt-4o"` | Model identifier                                                                     |
| `temperature` | float | `0.7`      | Sampling temperature (0-1)                                                           |
| `max_tokens`  | int   | `8192`     | Max response tokens                                                                  |
| `max_retries` | int   | `3`        | API retry attempts                                                                   |
| `prompt_path` | str   | varies     | Path to method prompts                                                               |
| `lang`        | str   | `"en"`     | Language code                                                                        |

## Creating Custom Therapists

You can create custom therapists by running the following command:

```bash
patienthub create generator.gen_agent_name=therapist generator.gen_agent_name=<agent_name>
```

This creates the following two files and registers the therapist in `__init__.py`:

- `patienthub/therapists/<agent_name>.py`
- `data/prompts/therapist/<agent_name>.yaml`

All therapists implement the `BaseTherapist` abstract base class (see `patienthub/therapists/base.py`).

## See Also

- [Creating Custom Agents](../../contributing/new-agents.md)
