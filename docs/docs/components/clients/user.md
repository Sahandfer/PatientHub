# User (Human-in-the-Loop)

The User client enables human participation in therapy simulations, allowing real people to act as clients/patients in interactive sessions.

## Overview

| Property  | Value                |
| --------- | -------------------- |
| **Key**   | `user`               |
| **Type**  | Human-in-the-loop    |
| **Focus** | Interactive Sessions |

## Description

The User client is a special agent type that delegates client responses to a human operator. This enables interactive training scenarios, human evaluation studies, and live demonstrations where a real person plays the role of a patient while interacting with therapist agents (either AI or human).

## Key Features

- **Real-time interaction** - Human provides responses in real-time
- **Full control** - Complete flexibility in presenting symptoms and behaviors
- **Training mode** - Ideal for standardized patient practice
- **Evaluation studies** - Enables human evaluation of therapist agents

## Configuration

### YAML Configuration

```yaml
client:
  agent_type: user
```

### Python Usage

```python
from patienthub.clients import get_client
from omegaconf import OmegaConf

config = OmegaConf.create({
    'agent_type': 'user'
})

client = get_client(configs=config, lang='en')
```

## Parameters

The User client does not require additional configuration parameters as it relies on human input.

## Use Cases

- **Standardized Patient Training** - Medical/psychology students practice with real SPs
- **Therapist Agent Evaluation** - Human clients evaluate AI therapist quality
- **Interactive Demonstrations** - Live demos at conferences or training sessions
- **Research Studies** - Controlled experiments with human participants
- **Quality Assurance** - Testing therapist agent responses to edge cases

## Integration

The User client integrates with PatientHub's interactive interfaces:

- **Chainlit Web Demo** - Provides a chat interface for human interaction
- **Command Line** - Text-based interaction through the terminal
- **Custom Interfaces** - Can be integrated with custom UIs

## Example Session

```python
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from omegaconf import OmegaConf

# Create human client
client_config = OmegaConf.create({'agent_type': 'user'})
client = get_client(configs=client_config, lang='en')

# Create AI therapist
therapist_config = OmegaConf.create(
    {
        "agent_type": "basic",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 8192,
        "max_retries": 3,
    }
)
therapist = get_therapist(configs=therapist_config, lang="en")

# Run interactive session
# Human provides client responses, AI provides therapist responses
```
