---
sidebar_position: 1
---

# Client Agents API

Client agents simulate patients in therapy conversations.

## Available Clients

| Client                                | Key            | Description                                 |
| ------------------------------------- | -------------- | ------------------------------------------- |
| [**SAPS**](./saps.md)                 | `saps`         | State-aware medical patient                 |
| [**ConsistentMI**](./consistentmi.md) | `consistentMI` | MI client with stage transitions (ACL 2025) |
| [**Eeyore**](./eeyore.md)             | `eeyore`       | Depression simulation (ACL 2025)            |
| [**AnnaAgent**](./annaagent.md)       | `annaAgent`    | Multi-session with memory (ACL 2025)        |
| [**AdaptiveVP**](./adaptivevp.md)     | `adaptiveVP`   | Nurse training simulation (ACL 2025)        |
| [**SimPatient**](./simpatient.md)     | `simPatient`   | Cognitive model updates (CHI 2025)          |
| [**TalkDep**](./talkdep.md)           | `talkDep`      | Depression screening (CIKM 2025)            |
| [**ClientCast**](./clientcast.md)     | `clientCast`   | Psychotherapy assessment                    |
| [**Psyche**](./psyche.md)             | `psyche`       | Psychiatric assessment                      |
| [**PatientPsi**](./patientpsi.md)     | `patientPsi`   | CBT-focused patient (EMNLP 2024)            |
| [**RoleplayDoh**](./roleplaydoh.md)   | `roleplayDoh`  | Principle-based simulation (EMNLP 2024)     |
| [**User**](./user.md)                 | `user`         | Human input client                          |

## Listing Available Clients

```python
from patienthub.clients import CLIENT_REGISTRY, CLIENT_CONFIG_REGISTRY

# List all client types
print("Available clients:", list(CLIENT_REGISTRY.keys()))

# Get config class for a client
config_class = CLIENT_CONFIG_REGISTRY['patientPsi']
print(config_class)
```

## Loading a Client

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 8192,
    'max_retries': 3,
    'prompt_path': 'data/prompts/client/patientPsi.yaml',
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
    'patient_type': 'upset',
})

client = get_client(configs=config, lang='en')
```

## Data Format

- Prompt Data is stored in `data/prompts/client`.
- Character data is stored in files under `data/characters`
- Each file is a JSON list; `data_idx` selects the entry to be simulated

## Configuration Options

### Common Options

| Option        | Type  | Default    | Description                                                                          |
| ------------- | ----- | ---------- | ------------------------------------------------------------------------------------ |
| `agent_type`  | str   | required   | Client type identifier                                                               |
| `model_type`  | str   | `"OPENAI"` | Model provider key (used to read `${MODEL_TYPE}_API_KEY` / `${MODEL_TYPE}_BASE_URL`) |
| `model_name`  | str   | `"gpt-4o"` | Model identifier                                                                     |
| `temperature` | float | `0.7`      | Sampling temperature (0-1)                                                           |
| `max_tokens`  | int   | `8192`     | Max response tokens                                                                  |
| `max_retries` | int   | `3`        | API retry attempts                                                                   |
| `prompt_path` | str   | varies     | Path to method prompts                                                               |
| `data_path`   | str   | varies     | Path to character JSON file                                                          |
| `data_idx`    | int   | `0`        | Index of character in file                                                           |
| `lang`        | str   | `"en"`     | Language code                                                                        |

## Response Format

Most clients return a structured response:

```python
from pydantic import BaseModel, Field

class Response(BaseModel):
    content: str = Field(
        description="The content of the patient's response"
    )
```

Some clients include additional fields:

```python
# PatientPsi response
class Response(BaseModel):
    content: str
    # Internal reasoning (not shown to therapist)

# ConsistentMI response
class Response(BaseModel):
    content: str
    action: str  # Selected action type
```

## By Focus Area

### Depression & Mood Disorders

- **Eeyore**: Realistic depression simulation with expert validation
- **TalkDep**: Clinically grounded personas for depression screening

### Motivational Interviewing

- **ConsistentMI**: Stage-of-change model with consistent behavior
- **SimPatient**: Cognitive model with internal state tracking

### General Psychotherapy

- **PatientPsi**: CBT-focused with cognitive distortions
- **RoleplayDoh**: Domain-expert created principles
- **ClientCast**: Assessment-focused simulation

### Specialized Training

- **AdaptiveVP**: Nurse communication training
- **SAPS**: Medical diagnosis training
- **Psyche**: Psychiatric assessment training

## Create New Clients

You can run the following command to create the necessary files for a new client:

```bash
uv run python -m examples.create generator.gen_agent_type=client generator.gen_agent_name=<agent_name>
```

This creates the following two files and registers the client in `__init__.py`:

- `patienthub/clients/<agent_name>.py`
- `data/prompts/client/<agent_name>.yaml`

All clients implement the `BaseClient` abstract base class (see `patienthub/clients/base.py`).

## See Also

- [Creating Custom Therapists](../../contributing/new-agents.md)
