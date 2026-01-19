---
sidebar_position: 1
---

# Client Agents API

Client agents simulate patients in therapy conversations.

## Available Clients

| Agent          | Description                                 | Config Class               |
| -------------- | ------------------------------------------- | -------------------------- |
| `patientPsi`   | CBT-focused patient (EMNLP 2024)            | `PatientPsiClientConfig`   |
| `consistentMI` | MI client with stage transitions (ACL 2025) | `ConsistentMIClientConfig` |
| `eeyore`       | Depression simulation (ACL 2025)            | `EeyoreClientConfig`       |
| `annaAgent`    | Multi-session with memory (ACL 2025)        | `AnnaAgentClientConfig`    |
| `adaptiveVP`   | Nurse training simulation (ACL 2025)        | `AdaptiveVPClientConfig`   |
| `simPatient`   | Cognitive model updates (CHI 2025)          | `SimPatientClientConfig`   |
| `talkDep`      | Depression screening (CIKM 2025)            | `TalkDepClientConfig`      |
| `clientCast`   | Psychotherapy assessment                    | `ClientCastClientConfig`   |
| `saps`         | State-aware medical patient                 | `SAPSClientConfig`         |
| `psyche`       | Psychiatric assessment                      | `PsycheClientConfig`       |
| `roleplayDoh`  | Principle-based simulation (EMNLP 2024)     | `RoleplayDohClientConfig`  |
| `basic`        | Simple baseline client                      | `BasicClientConfig`        |
| `user`         | Human input client                          | `UserClientConfig`         |

## Loading a Client

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
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
| `model_type`  | str   | `"LAB"`    | Model provider (`LAB`, `openai`, `huggingface`, `local`) |
| `model_name`  | str   | `"gpt-4o"` | Model identifier                                         |
| `temperature` | float | `0.7`      | Sampling temperature (0-1)                               |
| `max_tokens`  | int   | `1024`     | Max response tokens                                      |
| `max_retries` | int   | `3`        | API retry attempts                                       |
| `data_path`   | str   | varies     | Path to character JSON file                              |
| `data_idx`    | int   | `0`        | Index of character in file                               |
| `lang`        | str   | `"en"`     | Language code                                            |

### Client-Specific Options

#### ConsistentMI

```python
{
    'agent_type': 'consistentMI',
    'initial_stage': 'precontemplation',  # Stage of change model
    # Stages: precontemplation, contemplation, preparation, action, maintenance
}
```

#### SimPatient

```python
{
    'agent_type': 'simPatient',
    'continue_last_session': False,  # Resume from previous session
    'conv_history_path': 'data/sessions/SimPatient/session_1.json',
}
```

#### AdaptiveVP

```python
{
    'agent_type': 'adaptiveVP',
    # Uses stage direction for adaptive responses
}
```

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
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
}

test_message = "How have you been feeling lately?"

for agent_type in ['patientPsi', 'eeyore', 'consistentMI']:
    config = OmegaConf.create({
        **base_config,
        'agent_type': agent_type,
        'data_path': f'data/characters/{agent_type[0].upper() + agent_type[1:]}.json',
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

## Character Data Format

Character data is stored in JSON files under `data/characters/`:

```json
[
  {
    "demographics": {
      "name": "Alex",
      "age": 28,
      "gender": "male",
      "occupation": "software engineer"
    },
    "presenting_problem": "Feeling overwhelmed at work...",
    "mental_state": {
      "affect": "depressed, anxious",
      "cognition": {
        "core_beliefs": ["I am inadequate", "Others are more competent"],
        "negative_automatic_thoughts": [
          "I will fail",
          "They'll find out I'm a fraud"
        ]
      }
    },
    "personality": {
      "summary": "Introverted, perfectionistic",
      "neuroticism": 8,
      "extraversion": 3
    }
  }
]
```

## Extending Clients

See [Contributing: New Agents](/docs/contributing/new-agents) for how to create custom client implementations.
