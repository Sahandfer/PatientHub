# Events

Events in PatientHub manage the flow of interactions between agents. For instance, they orchestrate how clients, therapists, and other participants interact over time.

## Overview

Events provide:

- **Session Management** - Control conversation flow and turn-taking
- **State Tracking** - Maintain conversation history and session state
- **End Conditions** - Handle session termination logic
- **Output Handling** - Save session data for analysis

## Available Events

| Event                                       | Key               | Description                                                |
| ------------------------------------------- | ----------------- | ---------------------------------------------------------- |
| [**Therapy Session**](./therapy-session.md) | `therapy_session` | Standard therapy conversation between client and therapist |

## Usage

### CLI

```bash
uv run python -m examples.simulate event=therapy_session
```

### Python

```python
from patienthub.events import get_event

# With default configurations
event = get_event(name="therapy_session")

# With custom configurations
from omegaconf import OmegaConf
event_config = {
    'event_type': 'therapy_session',
    'max_turns': 30,
    'reminder_turn_num': 5,
    'output_dir': 'outputs/session.json',
}
event = get_event(name="therapy_session", configs=event_config)

# Run the event
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

## See Also

- [Simulations Guide](../../guide/simulations.md)
- [Creating Custom Agents](../../contributing/new-agents.md)
