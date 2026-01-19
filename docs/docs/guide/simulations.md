---
sidebar_position: 1
---

# Running Simulations

PatientHub provides multiple ways to run therapy session simulations.

## CLI Simulation

The simplest approach uses the command-line interface:

```bash
uv run python -m examples.simulate
```

### Customize Components

```bash
# Specify client and therapist
uv run python -m examples.simulate client=patientPsi therapist=CBT

# Add evaluation
uv run python -m examples.simulate client=patientPsi therapist=CBT evaluator=rating

# Adjust session parameters
uv run python -m examples.simulate event.max_turns=25 event.reminder_turn_num=5
```

## Python API

For programmatic control:

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.events import get_event

# Configure client
client_config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})

# Configure therapist
therapist_config = OmegaConf.create({
    'agent_type': 'CBT',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
})

# Configure session
event_config = OmegaConf.create({
    'event_type': 'therapySession',
    'max_turns': 20,
    'reminder_turn_num': 5,
    'output_dir': 'outputs/my_session.json',
})

# Load components
client = get_client(configs=client_config, lang='en')
therapist = get_therapist(configs=therapist_config, lang='en')
event = get_event(configs=event_config)

# Set up session
event.set_characters({
    'client': client,
    'therapist': therapist,
    'evaluator': None,
})

# Run simulation
event.start()
```

## Manual Turn-by-Turn

For fine-grained control over each turn:

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'consistentMI',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/ConsistentMI.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Therapist'})

# Simulate conversation
conversation = []
therapist_messages = [
    "Hi, thanks for coming in today. What brings you here?",
    "I see. Can you tell me more about that?",
    "How does that make you feel?",
    "What would you like to change about this situation?",
]

for msg in therapist_messages:
    print(f"Therapist: {msg}")
    conversation.append({'role': 'therapist', 'content': msg})

    response = client.generate_response(msg)
    print(f"Client: {response.content}\n")
    conversation.append({'role': 'client', 'content': response.content})

# Save conversation
import json
with open('outputs/manual_session.json', 'w') as f:
    json.dump({'messages': conversation}, f, indent=2)
```

## Human-in-the-Loop

Use the `user` therapist for manual input:

```bash
uv run python -m examples.simulate client=patientPsi therapist=user
```

Or in Python:

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'eeyore',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/Eeyore.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'You'})

print("Type 'quit' to exit\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break

    response = client.generate_response(user_input)
    print(f"Client: {response.content}\n")
```

## Session Events

The `TherapySession` event manages the simulation flow using LangGraph:

1. **initiate_session**: Set up client and therapist
2. **generate_therapist_response**: Get therapist's message
3. **generate_client_response**: Get client's response
4. **give_reminder**: Notify about remaining turns
5. **end_session**: Save session data

### Session State

```python
class TherapySessionState(TypedDict):
    messages: List[Dict[str, Any]]  # Conversation history
    summary: Optional[str]           # Session summary
    homework: Optional[List[str]]    # Assigned homework
    msg: Optional[str]               # Current message
```

## Output Format

Sessions are saved as JSON:

```json
{
  "profile": {
    "demographics": { "name": "Alex", "age": 28 },
    "presenting_problem": "..."
  },
  "messages": [
    { "role": "therapist", "content": "Hello, how are you?" },
    { "role": "client", "content": "I've been feeling..." }
  ],
  "num_turns": 15
}
```

## Next Steps

- [Batch Processing](/docs/guide/batch-processing) - Run multiple simulations
- [Evaluation](/docs/guide/evaluation) - Assess conversation quality
- [Web Demo](/docs/guide/web-demo) - Interactive interface
