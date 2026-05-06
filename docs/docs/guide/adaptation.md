---
sidebar_position: 2
---

# Adapting Character Profiles

PatientHub can convert a character profile from one client format to another using an LLM. This is useful when you want to reuse an existing character across clients that have different data schemas (e.g., converting a `patientPsi` profile into a `roleplayDoh` profile).

## CLI

```bash
patienthub adapt input_path=data/characters/PatientPsi.json target_client=roleplayDoh
```

This loads the first character in `PatientPsi.json`, infers the target structure from the `roleplayDoh` schema, and saves the result to `data/characters/adapted.json`.

### Options

| Parameter      | Default                          | Description                                                        |
| -------------- | -------------------------------- | ------------------------------------------------------------------ |
| `input_path`   | _(required)_                     | Path to the source character JSON file                             |
| `target_client`| _(required)_                     | Name of the target client (must be registered in the schema registry) |
| `source_index` | `0`                              | Index of the character to adapt within the source file             |
| `example_path` | `""`                             | Optional path to a few-shot example JSON for the target format     |
| `output_path`  | `data/characters/adapted.json`   | Path where the adapted character JSON will be saved                |
| `lang`         | `en`                             | Output language (`en`, `zh`, …)                                    |

### Examples

```bash
# Adapt the third character (index 2)
patienthub adapt \
  input_path=data/characters/PatientPsi.json \
  target_client=roleplayDoh \
  source_index=2

# Provide a few-shot example to guide the adaptation
patienthub adapt \
  input_path=data/characters/PatientPsi.json \
  target_client=roleplayDoh \
  example_path=data/characters/roleplayDoh.json

# Write output to a custom path
patienthub adapt \
  input_path=data/characters/PatientPsi.json \
  target_client=roleplayDoh \
  output_path=data/characters/adapted/psi_to_doh.json

# Generate content in Chinese
patienthub adapt \
  input_path=data/characters/PatientPsi.json \
  target_client=roleplayDoh \
  lang=zh
```

## How It Works

1. **Load source** — reads the character at `source_index` from `input_path`.
2. **Resolve target schema** — looks up the target client in the schema registry (`patienthub/schemas/__init__.py`) and extracts its JSON Schema definition.
3. **Optional few-shot example** — if `example_path` is set, the first entry in that file is included in the prompt as a concrete reference for structure and field meanings (the LLM is instructed not to copy its facts).
4. **LLM adaptation** — sends a structured prompt to the configured model. The model is asked to preserve source facts, conservatively fill in target-only fields, and return valid JSON.
5. **Save** — the result is appended to `output_path` (or written fresh if the file does not yet exist).

## Python API

```python
import json
from omegaconf import OmegaConf
from patienthub.schemas import get_profile_schema
from patienthub.utils import load_json, save_json, get_chat_model, parse_json_response
from jinja2 import Template

# Load source character
source_data = load_json("data/characters/PatientPsi.json")
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

| `target_client`  | Schema class              |
| ---------------- | ------------------------- |
| `patientPsi`     | `PatientPsiCharacter`     |
| `roleplayDoh`    | `RoleplayDohCharacter`    |
| `psyche`         | `PsycheCharacter`         |
| `simPatient`     | `SimPatientCharacter`     |
| `talkDep`        | `TalkDepCharacter`        |
| `adaptiveVP`     | `AdaptiveVPCharacter`     |
| `annaAgent`      | `AnnaAgentCharacter`      |
| `clientCast`     | `ClientCastCharacter`     |
| `eeyore`         | `EeyoreCharacter`         |
| `saps`           | `SAPSCharacter`           |
| `consistentMI`   | `ConsistentMICharacter`   |

## Output Format

The adapted character is saved as JSON matching the target client's schema. Repeated runs append new entries to the same file:

```json
{
  "description": "Alex is a male patient struggling with anxiety and avoidance behaviors..."
}
```

## Next Steps

- [Running Simulations](/docs/guide/simulations) — use the adapted character in a session
- [Evaluation](/docs/guide/evaluation) — assess simulation quality
