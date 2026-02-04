# Therapy Session

The Therapy Session event manages standard therapy conversations between a client and therapist agent.

## Overview

| Property  | Value                 |
| --------- | --------------------- |
| **Key**   | `therapySession`      |
| **Type**  | Conversation Event    |
| **Focus** | Client-Therapist Dyad |

## Description

The Therapy Session is the primary event type in PatientHub, orchestrating conversations between client and therapist agents. It manages turn-taking, tracks conversation state, handles end conditions, and saves session output for later analysis.

## Key Features

- **Turn Management** - Controls alternating responses between client and therapist
- **State Tracking** - Maintains full conversation history and metadata
- **End Conditions** - Multiple termination triggers (max turns, explicit end)
- **Reminders** - Notifies therapist when session is nearing end
- **Output Saving** - Automatically saves sessions in JSON format

## Configuration

### YAML Configuration

```yaml
event:
  event_type: therapySession
  max_turns: 30
  reminder_turn_num: 5
  output_dir: outputs/session.json
```

### Python Usage

```python
from omegaconf import OmegaConf
from patienthub.events import get_event

config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 30,
    'reminder_turn_num': 5,
    'output_dir': 'outputs/session.json',
})

event = get_event(configs=config)
```

## Parameters

| Parameter           | Type   | Default          | Description                       |
| ------------------- | ------ | ---------------- | --------------------------------- |
| `event_type`        | string | `therapySession` | Event type identifier             |
| `max_turns`         | int    | `30`             | Maximum conversation turns        |
| `reminder_turn_num` | int    | `5`              | Turns before end to show reminder |
| `output_dir`        | string | varies           | Output file path for session data |

## Session Flow

The TherapySession runs as a finite-state workflow:

```
START
  │
  ▼
init_session
  │
  ▼
generate_therapist_response
  │
  ▼
generate_client_response ──┬──► end_session (therapist says END/end/exit)
  │                        │
  ├──► end_session (num_turns >= max_turns)
  │
  └──► check_and_remind ──► generate_therapist_response
            │
            └── (adds reminder when turns_left <= reminder_turn_num)
```

## Session State

```python
from typing import TypedDict, List, Dict, Any

class TherapySessionState(TypedDict):
    messages: List[Dict[str, Any]]  # Conversation history
    msg: str                        # Current message being processed
    num_turns: int                  # Number of completed turns
    session_ended: bool             # End flag
    initialized: bool               # Init flag
    needs_reminder: bool            # Reminder flag
```

## Methods

### `set_characters(characters: Dict[str, Any])`

Set up the session participants:

```python
event.set_characters({
    'client': client_agent,
    'therapist': therapist_agent,
    'evaluator': evaluator_agent,  # Optional
})
```

### `start()`

Begin the session:

```python
event.start()
```

### `reset()`

Reset for a new session:

```python
event.reset()
```

## Output Format

Sessions are saved as JSON:

```json
{
  "profile": { "name": "Client" },
  "messages": [
    { "role": "therapist", "content": "Hello, how are you feeling today?" },
    { "role": "client", "content": "I've been really anxious lately..." }
  ],
  "num_turns": 15
}
```

## Complete Example

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.events import get_event
from patienthub.therapists import get_therapist
from patienthub.clients.patientPsi import PatientPsiClientConfig
from patienthub.therapists.eliza import ElizaTherapistConfig

# Create event
event_config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 10,
    'reminder_turn_num': 2,
    'output_dir': 'outputs/my_session.json',
})
event = get_event(configs=event_config)

# Load agents
client_config = OmegaConf.structured(PatientPsiClientConfig())
therapist_config = OmegaConf.structured(ElizaTherapistConfig())
client = get_client(configs=client_config, lang='en')
therapist = get_therapist(configs=therapist_config, lang='en')

# Set up characters
event.set_characters({
    'client': client,
    'therapist': therapist,
    'evaluator': None,
})

# Run session
event.start()
```

## CLI Usage

```bash
uv run python -m examples.simulate \
    client=patientPsi \
    therapist=eliza \
    event.max_turns=10 \
    event.output_dir=outputs/my_session.json
```

## Use Cases

- **Training Simulations** - Practice therapy conversations
- **Research Studies** - Generate conversation data for analysis
- **Agent Evaluation** - Test client and therapist agents
- **Demonstrations** - Interactive therapy demos
