---
sidebar_position: 1
---

# Client Agents API

Client agents simulate patients in therapy conversations.

## Available Clients

| Agent          | Description                                 | Config Class               |
| -------------- | ------------------------------------------- | -------------------------- |
| `saps`         | State-aware medical patient                 | `SAPSClientConfig`         |
| `consistentMI` | MI client with stage transitions (ACL 2025) | `ConsistentMIClientConfig` |
| `eeyore`       | Depression simulation (ACL 2025)            | `EeyoreClientConfig`       |
| `annaAgent`    | Multi-session with memory (ACL 2025)        | `AnnaAgentClientConfig`    |
| `adaptiveVP`   | Nurse training simulation (ACL 2025)        | `AdaptiveVPClientConfig`   |
| `simPatient`   | Cognitive model updates (CHI 2025)          | `SimPatientClientConfig`   |
| `talkDep`      | Depression screening (CIKM 2025)            | `TalkDepClientConfig`      |
| `clientCast`   | Psychotherapy assessment                    | `ClientCastClientConfig`   |
| `psyche`       | Psychiatric assessment                      | `PsycheClientConfig`       |
| `patientPsi`   | CBT-focused patient (EMNLP 2024)            | `PatientPsiClientConfig`   |
| `roleplayDoh`  | Principle-based simulation (EMNLP 2024)     | `RoleplayDohClientConfig`  |
| `user`         | Human input client                          | `UserClientConfig`         |

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
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
    'patient_type': 'upset',
})

client = get_client(configs=config, lang='en')
```

## Client Interface

All clients implement the `ChatAgent` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel

class ChatAgent(ABC):
    chat_model: Any
    data: Dict[str, Any]
    messages: List[str] | List[Dict[str, Any]]
    lang: str

    @abstractmethod
    def generate(
        self,
        messages: List[str] | List[Dict[str, Any]],
        response_format: Optional[Type[BaseModel]] = None,
    ) -> BaseModel | str:
        """Generate a response based on the input messages."""
        pass

    @abstractmethod
    def generate_response(self, msg: str) -> BaseModel:
        """Generate response to a single therapist message."""
        pass

    @abstractmethod
    def set_therapist(
        self,
        therapist: Dict[str, Any],
        prev_sessions: List[Dict[str, str]] | None = None
    ):
        """Set the therapist for the session."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the client to its initial state."""
        pass
```

## Configuration Options

### Common Options

| Option        | Type  | Default    | Description                                              |
| ------------- | ----- | ---------- | -------------------------------------------------------- |
| `agent_type`  | str   | required   | Client type identifier                                   |
| `model_type`  | str   | `"OPENAI"` | Model provider key (used to read `${MODEL_TYPE}_API_KEY` / `${MODEL_TYPE}_BASE_URL`) |
| `model_name`  | str   | `"gpt-4o"` | Model identifier                                         |
| `temperature` | float | `0.7`      | Sampling temperature (0-1)                               |
| `max_tokens`  | int   | `8192`     | Max response tokens                                      |
| `max_retries` | int   | `3`        | API retry attempts                                       |
| `data_path`   | str   | varies     | Path to character JSON file                              |
| `data_idx`    | int   | `0`        | Index of character in file                               |
| `lang`        | str   | `"en"`     | Language code                                            |

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

## Example: Comparing Clients

```python 
from patienthub.clients import get_client, CLIENT_REGISTRY
from omegaconf import OmegaConf

base_config = {
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 8192,
    'max_retries': 3,
}

test_message = "How have you been feeling lately?"

data_paths = {
    'saps': 'data/characters/SAPS.json',
    'talkDep': 'data/characters/talkDep.json',
    'psyche': 'data/characters/Psyche.json',
}

for agent_type in ['saps', 'talkDep', 'psyche']:
    config = OmegaConf.create({
        **base_config,
        'agent_type': agent_type,
        'data_path': data_paths[agent_type],
        'data_idx': 0,
    })
    try:
        client = get_client(configs=config, lang='en')
        client.set_therapist({'name': 'Therapist'})
        response = client.generate_response(test_message)
        print(f"\n=== {agent_type} ===")
        print(response.content[:200] + "..." if len(response.content) > 200 else response.content)
    except Exception as e:
        print(f"\n=== {agent_type} === Error: {e}")
```

## Listing Available Clients

```python
from patienthub.clients import CLIENT_REGISTRY, CLIENT_CONFIG_REGISTRY

# List all client types
print("Available clients:", list(CLIENT_REGISTRY.keys()))

# Get config class for a client
config_class = CLIENT_CONFIG_REGISTRY['patientPsi']
print(config_class)
```

## Data Format

Prompt Data is stored in `PatientHub/data/prompts/`. Character data is stored in files under `data/characters/`. Each file is a JSON list; `data_idx` selects one entry. The exact schema is client-specific (see the shipped files like `data/characters/PatientPsi.json` and the corresponding client implementation under `patienthub/clients/`).

## Extending Clients

See [Contributing: New Agents](/docs/contributing/new-agents) for how to create custom client implementations.
