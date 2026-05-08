# Generator Agents API

Generators create synthetic character files (profiles) for use with client agents.

## Available Generators

| Generator                                   | Key          | Description                                                        |
| ------------------------------------------- | ------------ | ------------------------------------------------------------------ |
| [**AnnaAgent Generator**](./annaagent.md)   | `annaAgent`  | Multi-session profiles with scales and memory states               |
| [**ClientCast Generator**](./clientcast.md) | `clientCast` | Profiles from conversation excerpts via Big Five + clinical scales |
| [**PatientZero Generator**](./patientzero.md) | `patientZero` | Disease-grounded synthetic patient records with sampled priors     |
| [**Psyche Generator**](./psyche.md)         | `psyche`     | MFC psychiatric profiles for assessment training                   |

## Listing Available Generators

```python
from patienthub.generators import GENERATORS, GENERATOR_CONFIG_REGISTRY

# List all generator types
print("Available generators:", list(GENERATORS.keys()))

# Get config class for a generator
config_class = GENERATOR_CONFIG_REGISTRY['psyche']
print(config_class)
```

## Loading a Generator

```python
from patienthub.generators import get_generator

generator = get_generator(agent_name='psyche', lang='en')
```

## Loading a Generator with Custom Configuration

```python
from omegaconf import OmegaConf
from patienthub.generators import get_generator

config = OmegaConf.create({
    'agent_name': 'psyche',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 8192,
    'max_retries': 3,
    'prompt_path': 'data/prompts/generator/psyche.yaml',
    'input_dir': 'data/resources/psyche_character.json',
    'output_dir': 'data/characters/Psyche MFC.json',
})

generator = get_generator(agent_name='psyche', configs=config, lang='en')
```

## Generating a Character

All generators expose a single `generate_character()` method that runs the full pipeline and saves the result to the configured output path:

```python
generator.generate_character()
```

## Configuration Options

### Common Options

| Option        | Type  | Default    | Description                                                                          |
| ------------- | ----- | ---------- | ------------------------------------------------------------------------------------ |
| `agent_name`  | str   | required   | Generator identifier                                                                 |
| `model_type`  | str   | `"OPENAI"` | Model provider key (used to read `${MODEL_TYPE}_API_KEY` / `${MODEL_TYPE}_BASE_URL`) |
| `model_name`  | str   | `"gpt-4o"` | Model identifier                                                                     |
| `temperature` | float | `0.7`      | Sampling temperature (0-1)                                                           |
| `max_tokens`  | int   | `8192`     | Max response tokens                                                                  |
| `max_retries` | int   | `3`        | API retry attempts                                                                   |
| `prompt_path` | str   | varies     | Path to generator prompts                                                            |
| `input_dir`   | str   | varies     | Path to input data / seed file                                                       |
| `output_dir`  | str   | varies     | Path where the generated character JSON is saved                                     |
| `lang`        | str   | `"en"`     | Language code                                                                        |

## See Also

- [Creating Custom Agents](../../contributing/new-agents.md)
