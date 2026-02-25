# Therapists

Therapist agents in PatientHub provide the therapeutic interventions during simulated conversations. They can range from sophisticated AI-powered therapists to simple rule-based systems, enabling various research and training scenarios.

## Available Therapists

| Therapist                 | Key      | Description                                                                                          |
| ------------------------- | -------- | ---------------------------------------------------------------------------------------------------- |
| [**Cami**](./cami.md)     | `cami`   | A Counselor Agent Supporting Motivational Interviewing through State Inference and Topic Exploration |
| [**Psyche**](./psyche.md) | `psyche` | A psychiatrist agent simulated using a structured prompt with explicit clinical assessment criteria. |
| [**Basic**](./basic.md)   | `basic`  | A prompt-deriven therapist for specific needs                                                        |
| [**Eliza**](./eliza.md)   | `eliza`  | Classic pattern-matching therapist based on the original ELIZA program                               |
| [**User**](./user.md)     | `user`   | Human-in-the-loop therapist for interactive sessions                                                 |

- Prompt Data is stored in `data/prompts/therapist`.

## Usage

### Listing Available Therapists

```python
from patienthub.therapists import THERAPIST_CONFIG_REGISTRY, THERAPIST_REGISTRY

# List all therapist types
print("Available therapists:", list(THERAPIST_REGISTRY.keys()))

# Get config class for a therapist
config_class = THERAPIST_CONFIG_REGISTRY['cami']
print(config_class)
```

### Loading a Therapist

```python
from omegaconf import OmegaConf

from patienthub.therapists import THERAPIST_REGISTRY, get_therapist

# Get available therapists
available = list(THERAPIST_REGISTRY.keys())

# Create a therapist
config = OmegaConf.create(
    {
        "agent_type": "basic",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "prompt_path": "data/prompts/therapist/CBT.yaml",
        "temperature": 0.7,
        "max_tokens": 8192,
        "max_retries": 3,
    }
)
therapist = get_therapist(configs=config, lang="en")
```

## Creating Custom Therapists

You can create custom therapists by running the following command:

```bash
uv run python -m examples.create generator.gen_agent_type=therapist generator.gen_agent_name=<agent_name>
```

This creates the following two files and registers the therapist in `__init__.py`:

- `patienthub/therapists/<agent_name>.py`
- `data/prompts/therapist/<agent_name>.yaml`

## See Also

- [Creating Custom Therapists](../../contributing/new-agents.md)
