---
sidebar_position: 2
---

# Adapting Character Profiles

PatientHub can convert a character profile from one client format to another using an LLM. This is useful when you want to reuse an existing character across clients that have different data schemas (e.g., converting a `patientPsi` profile into a `roleplayDoh` profile).

## CLI

```bash
patienthub adapt source_path=data/characters/patientPsi.json target_client=roleplayDoh
```

This loads the first character in `patientPsi.json`, infers the target structure from the `roleplayDoh` schema, and saves the result to `data/characters/roleplayDoh_from_patientPsi.json` (named `<target_client>_from_<source_stem>.json`).

### Options

| Parameter       | Default            | Description                                                                             |
| --------------- | ------------------ | --------------------------------------------------------------------------------------- |
| `source_path`   | _(required)_       | Path to the source character JSON file                                                  |
| `target_client` | _(required)_       | Name of the target client (must be registered in the schema registry)                   |
| `source_idx`    | `0`                | Index of the character to adapt; set to `-1` to batch-adapt every character             |
| `use_example`   | `false`            | Use the target client's existing character file as a an example                         |
| `output_dir`    | `data/characters/` | Directory where the adapted file (`<target_client>_from_<source_stem>.json`) is written |
| `lang`          | `en`               | Output language (`en`, `zh`, …)                                                         |
| `num_workers`   | `1`                | Number of parallel threads to use in batch mode                                         |

### Examples

```bash
# Adapt the third character (index 2)
patienthub adapt \
  source_path=data/characters/patientPsi.json \
  target_client=roleplayDoh \
  source_idx=2

# Batch-adapt every character in the file with 4 workers
patienthub adapt \
  source_path=data/characters/patientPsi.json \
  target_client=roleplayDoh \
  source_idx=-1 \
  num_workers=4

# Continue a batch run that was interrupted (resume from existing output)
patienthub adapt \
  source_path=data/characters/patientPsi.json \
  target_client=roleplayDoh \
  source_idx=-1 \
  num_workers=4 \
  resume=true

# Use the target client's existing character file as a few-shot example
patienthub adapt \
  source_path=data/characters/patientPsi.json \
  target_client=roleplayDoh \
  use_example=true

# Write output to a custom directory
patienthub adapt \
  source_path=data/characters/patientPsi.json \
  target_client=roleplayDoh \
  output_dir=data/characters/adapted/

# Generate output in a different language (e.g., Chinese)
patienthub adapt \
  source_path=data/characters/patientPsi.json \
  target_client=roleplayDoh \
  lang=zh
```

## How It Works

1. **Load source**: reads the character at `source_idx` from `source_path` (or every character when `source_idx=-1`).
2. **Resolve target schema**: looks up the target client in the schema registry (`patienthub/schemas/__init__.py`) and extracts its JSON Schema definition.
3. **Optional few-shot example**: when `use_example=true`, an example from the target client's existing character file (`data/characters/<target_client>.json`) is included in the prompt as a concrete reference for structure and field meanings (the LLM is instructed not to copy its facts).
4. **LLM adaptation**: sends a structured prompt to the configured model. The model is asked to preserve source facts, conservatively fill in target-only fields, and return valid JSON.
5. **Validate & save**: the model output is validated against the target schema; invalid results are rejected (in batch mode they are counted as failures). Valid characters are written to `<output_dir>/<target_client>_from_<source_stem>.json`.

## Python API

```python
import json
from omegaconf import OmegaConf
from patienthub.schemas import get_profile_schema
from patienthub.utils import load_json, save_json, get_chat_model, parse_json_response
from jinja2 import Template

# Load source character
source_data = load_json("data/characters/patientPsi.json")
source_character = source_data[0]

# Resolve target schema
target_schema = get_profile_schema("roleplayDoh")
target_schema_json = json.dumps(target_schema.model_json_schema(), indent=2)

# Build prompt (mirrors the inline ADAPT_PROMPT in adapt.py)
prompt = f"""
You are adapting a PatientHub character profile from one client format to another.

Target client: roleplayDoh

...

Source character JSON:
{json.dumps(source_character, indent=2)}

Target schema (JSON Schema):
{target_schema_json}
"""

# Run the model
config = OmegaConf.create({
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 8192,
    "max_retries": 3,
    "lang": "en",
})

chat_model = get_chat_model(config)
result = chat_model.generate([{"role": "system", "content": prompt}])
adapted = parse_json_response(result.content)

save_json(adapted, "data/characters/adapted/result.json", overwrite=False)
```

## Supported Target Clients

Any client registered in the schema registry can be used as `target_client`:

| `target_client` | Schema class            |
| --------------- | ----------------------- |
| `patientPsi`    | `PatientPsiCharacter`   |
| `roleplayDoh`   | `RoleplayDohCharacter`  |
| `psyche`        | `PsycheCharacter`       |
| `simPatient`    | `SimPatientCharacter`   |
| `talkDep`       | `TalkDepCharacter`      |
| `adaptiveVP`    | `AdaptiveVPCharacter`   |
| `annaAgent`     | `AnnaAgentCharacter`    |
| `clientCast`    | `ClientCastCharacter`   |
| `eeyore`        | `EeyoreCharacter`       |
| `saps`          | `SAPSCharacter`         |
| `consistentMI`  | `ConsistentMICharacter` |

## Output Format

The adapted character is saved as JSON matching the target client's schema. Repeated runs append new entries to the same file:

```json
{
  "description": "Alex is a male patient struggling with anxiety and avoidance behaviors..."
}
```

## Next Steps

- [Running Simulations](/docs/guide/simulations): use the adapted character in a session
- [Evaluation](/docs/guide/evaluation): assess simulation quality
