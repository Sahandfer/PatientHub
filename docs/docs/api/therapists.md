---
sidebar_position: 2
---

# Therapist Agents API

Therapist agents simulate or interface with therapists in conversations.

## Available Therapists

| Agent   | Description                                | Config Class           |
| ------- | ------------------------------------------ | ---------------------- |
| `CBT`   | Cognitive Behavioral Therapy therapist     | `CBTTherapistConfig`   |
| `MI`    | Motivational Interviewing therapist        | `MITherapistConfig`    |
| `basic` | Simple AI therapist                        | `BasicTherapistConfig` |
| `eliza` | Classic Eliza chatbot                      | `ElizaTherapistConfig` |
| `bad`   | Intentionally poor therapist (for testing) | `BadTherapistConfig`   |
| `user`  | Human input                                | `UserTherapistConfig`  |

## Loading a Therapist

```python
from omegaconf import OmegaConf
from patienthub.therapists import get_therapist

config = OmegaConf.create({
    'agent_type': 'CBT',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
})

therapist = get_therapist(configs=config, lang='en')
```

## Therapist Interface

All therapists implement the `ChatAgent` interface:

```python
class ChatAgent(ABC):
    @abstractmethod
    def generate(self, messages, response_format) -> BaseModel:
        """Generate a response given message history."""
        pass

    @abstractmethod
    def generate_response(self, msg: str) -> Response:
        """Generate response to a client message."""
        pass

    @abstractmethod
    def set_client(self, client: Dict, prev_sessions=None):
        """Set the client for the session."""
        pass

    @abstractmethod
    def reset(self):
        """Reset the therapist state."""
        pass
```

## Configuration Options

### Common Options

| Option        | Type  | Default    | Description               |
| ------------- | ----- | ---------- | ------------------------- |
| `agent_type`  | str   | required   | Therapist type identifier |
| `model_type`  | str   | `"LAB"`    | Model provider            |
| `model_name`  | str   | `"gpt-4o"` | Model identifier          |
| `temperature` | float | `0.7`      | Sampling temperature      |
| `max_tokens`  | int   | `1024`     | Max response tokens       |
| `max_retries` | int   | `3`        | API retry attempts        |

## CBT Therapist

The CBT therapist uses cognitive behavioral therapy techniques:

```python
config = OmegaConf.create({
    'agent_type': 'CBT',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
})

therapist = get_therapist(configs=config, lang='en')
therapist.set_client({'name': 'Alex'})

response = therapist.generate_response("I feel like a failure at work.")
print(response.content)
# Example: "I hear that you're feeling like a failure.
#           Can you tell me about a specific situation that made you feel this way?"
```

### CBT Response Format

```python
class Response(BaseModel):
    reasoning: str = Field(
        description="The reasoning behind the response (internal)"
    )
    content: str = Field(
        description="The therapist's response to the client"
    )
```

## MI Therapist

The MI (Motivational Interviewing) therapist uses OARS techniques:

- **O**pen questions
- **A**ffirmations
- **R**eflections
- **S**ummaries

```python
config = OmegaConf.create({
    'agent_type': 'MI',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
})

therapist = get_therapist(configs=config, lang='en')
```

### MI Response Format

```python
class MIResponse(BaseModel):
    technique: str = Field(
        description="MI technique: 'open_question', 'affirmation', 'reflection', or 'summary'"
    )
    reasoning: str = Field(
        description="Brief reasoning for technique choice"
    )
    content: str = Field(
        description="The therapist's response"
    )
```

## User Therapist

For human-in-the-loop simulation:

```python
config = OmegaConf.create({
    'agent_type': 'user',
    'lang': 'en',
})

therapist = get_therapist(configs=config, lang='en')
therapist.set_client({'name': 'Patient'})

# Will prompt for input
response = therapist.generate_response("I've been feeling anxious.")
# Therapist response: [user types input]
```

## Eliza Therapist

Classic pattern-matching chatbot:

```python
config = OmegaConf.create({
    'agent_type': 'eliza',
    'lang': 'en',
})

therapist = get_therapist(configs=config, lang='en')
response = therapist.generate_response("I am feeling sad.")
# "Why do you say you are feeling sad?"
```

## Example: Full Session

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.therapists import get_therapist

# Set up client
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

# Set up therapist
therapist_config = OmegaConf.create({
    'agent_type': 'CBT',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
})

client = get_client(configs=client_config, lang='en')
therapist = get_therapist(configs=therapist_config, lang='en')

# Connect them
client.set_therapist({'name': therapist.name})
therapist.set_client({'name': client.name})

# Simulate conversation
conversation = []
therapist_msg = "Hello, thank you for coming in today. How are you feeling?"

for turn in range(5):
    print(f"Therapist: {therapist_msg}")
    conversation.append({'role': 'therapist', 'content': therapist_msg})

    client_response = client.generate_response(therapist_msg)
    print(f"Client: {client_response.content}\n")
    conversation.append({'role': 'client', 'content': client_response.content})

    therapist_response = therapist.generate_response(client_response.content)
    therapist_msg = therapist_response.content
```

## Listing Available Therapists

```python
from patienthub.therapists import THERAPIST_REGISTRY

print("Available therapists:", list(THERAPIST_REGISTRY.keys()))
```

## Creating Custom Therapists

See [Contributing: New Agents](/docs/contributing/new-agents) for how to add new therapist implementations.
