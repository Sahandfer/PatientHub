---
sidebar_position: 1
---

# Running Simulations

PatientHub provides multiple ways to run therapy session simulations.

## CLI Simulation

The simplest approach uses the command-line interface:

```bash
uv run python -m examples.simulate client=user therapist=eliza
```

### Customize Components

```bash
# Specify client and therapist
uv run python -m examples.simulate client=patientPsi therapist=basic

# Attach an evaluator (note: TherapySession does not execute it; see Evaluation guide)
uv run python -m examples.simulate client=patientPsi therapist=basic +evaluator=llm_judge

# Adjust session parameters
uv run python -m examples.simulate event.max_turns=25 event.reminder_turn_num=5
```

## Python API

For programmatic control:

```python
from patienthub.clients import get_client
from patienthub.events.therapySession import TherapySession
from patienthub.therapists import get_therapist
from omegaconf import OmegaConf

# Configure client
client_config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'patient_type': 'upset',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'prompt_path': 'data/prompts/client/patientPsi.yaml',
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})

# Configure therapist
therapist_config = OmegaConf.create({
    'agent_type': 'basic',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'prompt_path': 'data/prompts/therapist/CBT.yaml',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
})

# Configure session
event_config = OmegaConf.create({
    'max_turns': 20,
    'reminder_turn_num': 5,
    'output_dir': 'outputs/my_session.json',
})

# Load components
client = get_client(configs=client_config, lang='en')
therapist = get_therapist(configs=therapist_config, lang='en')
event = TherapySession(configs=event_config)

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
from patienthub.clients import get_client
from omegaconf import OmegaConf

config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'patient_type': 'upset',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/PatientPsi.json',
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
from patienthub.utils import save_json
save_json({'messages': conversation}, 'outputs/manual_session.json', overwrite=True)
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
    'model_type': 'LOCAL',
    'model_name': 'hosted_vllm//data3/public_checkpoints/huggingface_models/Eeyore_llama3.1_8B',
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

The `TherapySession` event manages the simulation flow using a Burr state machine:

1. **init_session**: Set up client and therapist
2. **generate_therapist_response**: Get therapist's message
3. **generate_client_response**: Get client's response
4. **check_and_remind**: Notify about remaining turns
5. **end_session**: Save session data

### Session State

```python
from typing import TypedDict, List, Dict, Any, Optional

class TherapySessionState(TypedDict):
    messages: List[Dict[str, Any]]  # Conversation history
    msg: Optional[str]               # Current message
    num_turns: int
    session_ended: bool
    initialized: bool
    needs_reminder: bool
```

## Output Format

Sessions are saved as JSON:

```json
{
  "profile": {
    "name": "Alex",
    "id": "1-1"
  },
  "messages": [
    { "role": "therapist", "content": "Hello, how are you?" },
    { "role": "client", "content": "I've been feeling..." }
  ],
  "num_turns": 15
}
```

## Next Steps

- [Evaluation](/docs/guide/evaluation) - Assess conversation quality
- [Web Demo](/docs/guide/web-demo) - Interactive interface
