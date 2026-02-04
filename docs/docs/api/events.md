---
sidebar_position: 4
---

# Events API

Events manage the flow of therapy sessions and other interactions.

## Available Events

| Event            | Description              | Config Class           |
| ---------------- | ------------------------ | ---------------------- |
| `therapySession` | Standard therapy session | `TherapySessionConfig` |

## TherapySession

The main event type for simulating therapy conversations.

### Configuration

```python
from omegaconf import OmegaConf

config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 30,
    'reminder_turn_num': 5,
    'output_dir': 'data/sessions/default/session_1.json',
})
```

### Configuration Options

| Option              | Type | Default            | Description                       |
| ------------------- | ---- | ------------------ | --------------------------------- |
| `event_type`        | str  | `"therapySession"` | Event type identifier             |
| `max_turns`         | int  | `30`               | Maximum conversation turns        |
| `reminder_turn_num` | int  | `5`                | Turns before end to show reminder |
| `output_dir`        | str  | varies             | Output file path                  |

### Usage

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.events import get_event
from patienthub.therapists import get_therapist
from patienthub.clients.patientPsi import PatientPsiClientConfig
from patienthub.therapists.eliza import ElizaTherapistConfig

# Before running:
# - set OPENAI_API_KEY (required)
# - set OPENAI_BASE_URL (optional)
# You can export them or put them in PatientHub/.env and run from the PatientHub directory.

# Create event
event_config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 1,
    'reminder_turn_num': 1,
    'output_dir': 'outputs/my_session.json',
})
event = get_event(configs=event_config)

# Load agents (calls an LLM for the client agent)
client_config = OmegaConf.structured(PatientPsiClientConfig())
therapist_config = OmegaConf.structured(ElizaTherapistConfig())
client = get_client(configs=client_config, lang='en')
therapist = get_therapist(configs=therapist_config, lang='en')

# Set up characters
event.set_characters({
    'client': client,
    'therapist': therapist,
    'evaluator': None,  # Optional
})

# Run session
event.start()
```

### Run via CLI (Hydra)

```bash
python -m examples.simulate client=patientPsi therapist=eliza event.max_turns=1 event.output_dir=outputs/my_session.json
```

### Session Flow

The TherapySession is implemented as a finite-state workflow and runs until an end condition is met:

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
            └── (adds a reminder when turns_left <= reminder_turn_num)
```

### Session State

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

### Methods

#### `set_characters(characters: Dict[str, Any])`

Set up the session participants:

```python
event.set_characters({
    'client': client_agent,
    'therapist': therapist_agent,
    'evaluator': evaluator_agent,  # Optional
})
```

#### `start()`

Begin the session:

```python
event.start()
```

#### `reset()`

Reset for a new session:

```python
event.reset()
```

### Output Format

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
