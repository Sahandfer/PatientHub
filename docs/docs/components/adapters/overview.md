---
sidebar_position: 1
---

# Adapter API

Adapters convert one client's character profile into another client's character format.

## Overview

PatientHub clients do not share a single character schema. `patientPsi`, `annaAgent`, `clientCast`, `psyche`, and others expect different profile fields and nested structures.

The adapter layer solves this by:

1. Validating the source character with the source client's Pydantic schema
2. Showing the model a real target-client character example as one-shot guidance
3. Constraining the generated output with the target client's Pydantic schema via `response_format`
4. Saving the converted profile in the target client's expected JSON container format

## Supported Clients

All currently registered non-`user` clients can participate in adapter conversion.

```python
from patienthub.adapters import CHARACTER_MODEL_REGISTRY

print(sorted(CHARACTER_MODEL_REGISTRY.keys()))
```

## CLI Usage

Use the minimal adapter entrypoint:

```bash
python -m examples.adapter source_client=patientPsi target_client=annaAgent
```

### Common Options

```bash
python -m examples.adapter \
  source_client=patientPsi \
  target_client=annaAgent \
  input_path=data/characters/PatientPsi.json \  # optional
  output_path=data/characters/AnnaAgent_from_patientPsi.json \  # optional
  source_idx=0 \
  model_type=OPENAI \
  model_name=gpt-4o
```

## Python API

```python
from omegaconf import OmegaConf
from patienthub.adapters import AdapterConfig, CharacterAdapter

configs = OmegaConf.structured(
    AdapterConfig(
        source_client="patientPsi",
        target_client="annaAgent",
        input_path="data/characters/PatientPsi.json",
        output_path="data/characters/AnnaAgent_from_patientPsi.json",
    )
)

adapter = CharacterAdapter(configs)
payload = adapter.adapt()
adapter.save(payload)
```

## Path Resolution

- `input_path` is optional. If omitted, the adapter reads from the source client's default `data_path`.
- `output_path` is optional. If omitted, the adapter writes beside the target client's default character file using a `_from_<source_client>` suffix.
- `source_idx` is used when the source file contains a JSON list.

## Output Rules

- The source payload is always validated against the source client's adapter schema before conversion.
- The target payload must satisfy the target client's adapter schema or the generation call fails.
- The saved JSON container follows the target client:
  - `simPatient` is saved as a single JSON object
  - other current clients are saved as JSON lists

## Adding Support for a New Client

When you create a new client with `examples.create`, PatientHub also scaffolds a matching adapter schema module:

```bash
python -m examples.create agent_type=client agent_name=myClient
```

This creates:

- `patienthub/clients/myClient.py`
- `data/prompts/client/myClient.yaml`
- `patienthub/adapters/myClient.py`

You then fill in `patienthub/adapters/myClient.py` with the Pydantic character schema for that client.

## See Also

- [Running Simulations](../../guide/simulations.md)
- [Adding New Agents](../../contributing/new-agents.md)
