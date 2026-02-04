# Events

Events in PatientHub manage the flow of therapy sessions and other interactions between agents. They orchestrate how clients, therapists, and other participants interact over time.

## Overview

Events provide:

- **Session Management** - Control conversation flow and turn-taking
- **State Tracking** - Maintain conversation history and session state
- **End Conditions** - Handle session termination logic
- **Output Handling** - Save session data for analysis

## Available Events

| Event                                       | Key              | Description                                                |
| ------------------------------------------- | ---------------- | ---------------------------------------------------------- |
| [**Therapy Session**](./therapy-session.md) | `therapySession` | Standard therapy conversation between client and therapist |

## Usage

### In Configuration

```yaml
event:
  event_type: therapySession
  max_turns: 30
  reminder_turn_num: 5
  output_dir: outputs/session.json
```

### In Code

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

## Running Events

### Command Line

```bash
uv run python -m examples.simulate \
    client=patientPsi \
    therapist=cbt \
    event.max_turns=30
```

### Programmatic Usage

```python
from patienthub.events import get_event
from patienthub.clients import get_client
from patienthub.therapists import get_therapist

# Create event
event = get_event(configs=event_config)

# Set up participants
event.set_characters({
    'client': client,
    'therapist': therapist,
    'evaluator': None,  # Optional
})

# Run session
event.start()
```

## Creating Custom Events

You can create custom events by extending the base class:

```python
from patienthub.events.base import Event

class MyCustomEvent(Event):
    def __init__(self, config):
        super().__init__(config)
        # Initialize your event

    def start(self):
        # Implement event logic
        pass
```

Then register it:

```python
from patienthub.events import EventRegistry

EventRegistry.register("my_event", MyCustomEvent)
```

## See Also

- [Simulations Guide](../../guide/simulations.md)
- [Creating Custom Agents](../../contributing/new-agents.md)
