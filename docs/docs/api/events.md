---
sidebar_position: 4
---

# Events API

Events manage the flow of therapy sessions and other interactions.

## Available Events

| Event            | Description              | Config Class           |
| ---------------- | ------------------------ | ---------------------- |
| `therapySession` | Standard therapy session | `TherapySessionConfig` |
| `interview`      | Structured interview     | `InterviewConfig`      |

## TherapySession

The main event type for simulating therapy conversations.

### Configuration

```python
from omegaconf import OmegaConf

config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 30,
    'reminder_turn_num': 5,
    'langfuse': False,
    'recursion_limit': 1000,
    'output_dir': 'data/sessions/default/session_1.json',
})
```

### Configuration Options

| Option              | Type | Default            | Description                       |
| ------------------- | ---- | ------------------ | --------------------------------- |
| `event_type`        | str  | `"therapySession"` | Event type identifier             |
| `max_turns`         | int  | `30`               | Maximum conversation turns        |
| `reminder_turn_num` | int  | `5`                | Turns before end to show reminder |
| `langfuse`          | bool | `False`            | Enable Langfuse tracing           |
| `recursion_limit`   | int  | `1000`             | LangGraph recursion limit         |
| `output_dir`        | str  | varies             | Output file path                  |

### Usage

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.events import get_event

# Load components
client = get_client(configs=client_config, lang='en')
therapist = get_therapist(configs=therapist_config, lang='en')

# Create event
event_config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 20,
    'output_dir': 'outputs/my_session.json',
})
event = get_event(configs=event_config)

# Set up characters
event.set_characters({
    'client': client,
    'therapist': therapist,
    'evaluator': None,  # Optional
})

# Run session
event.start()
```

### Session Flow

The TherapySession uses LangGraph to manage the conversation flow:

```
START
  │
  ▼
initiate_session
  │
  ▼
generate_therapist_response ◄──┐
  │                            │
  ▼                            │
generate_client_response       │
  │                            │
  ├─── CONTINUE ───────────────┘
  │
  ├─── REMIND ──► give_reminder ──► generate_therapist_response
  │
  └─── END ──► end_session
                   │
                   ▼
                  END
```

### Session State

```python
from typing import TypedDict, List, Dict, Any, Optional

class TherapySessionState(TypedDict):
    messages: List[Dict[str, Any]]  # Conversation history
    summary: Optional[str]           # Session summary (if generated)
    homework: Optional[List[str]]    # Assigned homework
    msg: Optional[str]               # Current message being processed
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
  "profile": {
    "demographics": { "name": "Alex", "age": 28 },
    "presenting_problem": "Anxiety at work"
  },
  "messages": [
    { "role": "therapist", "content": "Hello, how are you feeling today?" },
    { "role": "client", "content": "I've been really anxious lately..." }
  ],
  "num_turns": 15
}
```

## Interview Event

For structured interviews with predetermined questions.

### Configuration

```python
config = OmegaConf.create({
    'event_type': 'interview',
    'num_questions': 5,
    'langfuse': False,
    'output_dir': 'data/interviews/default/interview_1.json',
})
```

### Interview State

```python
class InterviewState(TypedDict):
    questions: List[str]          # List of questions
    answers: List[str]            # Collected answers
    current_question: Optional[str]
    msg: Optional[str]
```

### Usage

```python
from patienthub.events import get_event
from patienthub.clients import get_client
from patienthub.evaluators import get_evaluator

# Load interviewee (client)
interviewee = get_client(configs=client_config, lang='en')

# Load interviewer (evaluator with questions)
interviewer = get_evaluator(configs=eval_config, lang='en')

# Create interview event
event = get_event(configs=interview_config)
event.set_characters({
    'interviewee': interviewee,
    'interviewer': interviewer,
})

event.start()
```

## Custom Events

Create custom events by extending the base pattern:

```python
from dataclasses import dataclass
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END


@dataclass
class MyEventConfig:
    event_type: str = "myEvent"
    # ... custom options


class MyEventState(TypedDict):
    # ... define state


class MyEvent:
    def __init__(self, configs):
        self.configs = configs
        self.graph = self.build_graph()

    def set_characters(self, characters: Dict[str, Any]):
        # Store characters
        pass

    def build_graph(self):
        graph = StateGraph(MyEventState)

        # Add nodes
        graph.add_node("step1", self.step1)
        graph.add_node("step2", self.step2)

        # Add edges
        graph.add_edge(START, "step1")
        graph.add_edge("step1", "step2")
        graph.add_edge("step2", END)

        return graph.compile()

    def step1(self, state):
        # ... implementation
        return state

    def step2(self, state):
        # ... implementation
        return state

    def start(self):
        self.graph.invoke(input={})
```

Register in `patienthub/events/__init__.py`:

```python
from .myEvent import MyEvent, MyEventConfig

EVENT_REGISTRY = {
    'therapySession': TherapySession,
    'interview': Interview,
    'myEvent': MyEvent,
}
```

## Langfuse Integration

Enable tracing for debugging and analysis:

```python
config = OmegaConf.create({
    'event_type': 'therapySession',
    'langfuse': True,
    # ...
})
```

Set environment variables:

```bash
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```
