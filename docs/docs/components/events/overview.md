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
patienthub simulate event=therapy_session
```

### Python

```python
from patienthub.events import get_event

# With default configurations
event = get_event(event_name="therapy_session")

# With custom configurations
from omegaconf import OmegaConf
event_config = {
    'event_type': 'therapy_session',
    'max_turns': 30,
    'reminder_turn_num': 5,
    'output_dir': 'outputs/session.json',
}
event = get_event(event_name="therapy_session", configs=event_config)

# Run the event
event.start()

```

## Creating Custom Events

Events are plain Python classes (like `TherapySession`) — there is no shared `Event` base class to inherit from. A custom event implements a `set_characters(characters: dict)` method to receive its participants and a `start()` method to run the interaction:

```python
class MyCustomEvent:
    def __init__(self, configs):
        self.configs = configs
        # Initialize your event

    def set_characters(self, characters: dict):
        # Store participating agents (e.g. client, therapist)
        self.characters = characters

    def start(self):
        # Implement event logic
        pass
```

Register the class in `EVENT_REGISTRY` (and its config dataclass in `EVENT_CONFIG_REGISTRY`) in `patienthub/events/__init__.py` so it can be loaded via `get_event()`.

## See Also

- [Simulations Guide](../../guide/simulations.md)
- [Creating Custom Agents](../../contributing/new-agents.md)
