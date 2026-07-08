# Generator Agents API

Generators are pure transformers: each exposes `generate_character(data=None)` and
returns a character object. Generators do **no** file I/O — they do not read seed
lists and do not save output. The `generate` CLI owns all I/O (loading seeds,
driving the loop, and saving results).

## Available Generators

| Generator                           | Key           | Description                                                              |
| ----------------------------------- | ------------- | ------------------------------------------------------------------------ |
| [**AnnaAgent**](./annaagent.md)     | `annaAgent`   | Multi-session profiles with scales and memory states                     |
| [**ClientCast**](./clientcast.md)   | `clientCast`  | Profiles from conversation excerpts via Big Five + clinical scales       |
| [**Deprofile**](./deprofile.md)     | `deprofile`   | Clinical/social profile assembly with matched timelines and memory cards |
| [**PatientZero**](./patientzero.md) | `patientZero` | Disease-grounded synthetic patient records with sampled priors           |
| [**Psyche**](./psyche.md)           | `psyche`      | MFC psychiatric profiles for assessment training                         |

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
})

generator = get_generator(agent_name='psyche', configs=config, lang='en')
```

## Generating a Character

Every generator exposes a single `generate_character(data=None)` method that runs
the full pipeline and **returns** a character object. It performs no file I/O:

```python
character = generator.generate_character(seed_record)
```

In normal use you do not call this directly — the `generate` CLI drives the loop
and saves the returned characters, while each generator validates its own seed
record first (see below).

## Running Generation via the CLI

The `generate` CLI owns all I/O: it loads seed records, drives the loop, and saves
the results. Each record is first validated against the generator's own seed schema
via `BaseGenerator.prepare_seed`, then passed to `generate_character()`.

```bash
# Item-driven: one character per record in an input JSON list
patienthub generate generator=clientCast input_path=data/seeds/clientCast.json

# Config-parameterized (no input list): one character built from config
patienthub generate generator=patientZero generator.disease_key=depression

# Several samples appended to the output bank
patienthub generate generator=patientZero num_samples=10

# Custom output location + parallel workers, with resume
patienthub generate generator=clientCast input_path=data/seeds/clientCast.json \
    output_path=data/characters/clientCast.json num_workers=4 resume=true
```

### CLI I/O Options

| Option        | Type | Default                            | Description                                                                                             |
| ------------- | ---- | ---------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `generator`   | str  | required                           | Generator to run (e.g. `clientCast`, `psyche`)                                                          |
| `input_path`  | str  | `""`                               | Optional JSON list of seed records. When set, one character is produced per record, index-aligned       |
| `output_path` | str  | `data/characters/<agent_name>.json` | Where the generated characters are saved                                                                |
| `num_samples` | int  | `1`                                | Number of characters to generate when `input_path` is empty (appended to the output bank)               |
| `num_workers` | int  | `1`                                | Parallel workers (each builds its own generator instance)                                               |
| `resume`      | bool | `false`                            | With `input_path`: keep characters already in the output and only refill null (failed/pending) slots    |
| `lang`        | str  | `"en"`                             | Language code                                                                                           |
| `verbose`     | bool | `false`                            | Enable debug logging                                                                                    |

**With `input_path`**: one character per seed record, index-aligned and resume-aware
— failed or pending slots are saved as `null` and refilled on a later `resume` run.
Each seed record is validated against the generator's seed schema before generation;
a malformed record fails only that item.

**Without `input_path`**: `num_samples` characters are built from config and appended
to the output bank. `resume` does not apply in this mode.

## Seeds vs. Resources

PatientHub separates two kinds of generator input:

- **Seeds** (`data/seeds/<agent_name>.json`) are the per-character generation inputs
  the CLI reads via `input_path` — a JSON list where each record produces one
  character. Each generator's seed record shape is defined by its seed schema (see
  the per-generator pages).
- **Resources** (`data/resources/`) are shared reference knowledge a method consults
  during generation (event databases, symptom item definitions, disease priors, etc.).
  These are configured per generator (e.g. `resource_dir`) or shared as importable
  constants in `patienthub.resources`, and are not per-character.

Generated outputs are written to `data/characters/`.

## Generator Configuration Options

Every generator inherits the shared model options; each also has method-specific
fields documented on its own page.

| Option        | Type  | Default    | Description                                                                          |
| ------------- | ----- | ---------- | ------------------------------------------------------------------------------------ |
| `agent_name`  | str   | required   | Generator identifier                                                                 |
| `model_type`  | str   | `"OPENAI"` | Model provider key (used to read `${MODEL_TYPE}_API_KEY` / `${MODEL_TYPE}_BASE_URL`) |
| `model_name`  | str   | `"gpt-4o"` | Model identifier                                                                     |
| `temperature` | float | `0.7`      | Sampling temperature (0-1)                                                           |
| `max_tokens`  | int   | `8192`     | Max response tokens                                                                  |
| `max_retries` | int   | `3`        | API retry attempts                                                                   |
| `prompt_path` | str   | varies     | Path to generator prompts                                                            |
| `lang`        | str   | `"en"`     | Language code                                                                        |

## See Also

- [Creating Custom Agents](../../contributing/new-agents.md)
