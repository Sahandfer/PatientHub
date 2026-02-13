# User (Human-in-the-Loop)

The User therapist enables human participation in therapy simulations, allowing real people to act as therapists in interactive sessions.

## Overview

| Property  | Value                |
| --------- | -------------------- |
| **Key**   | `user`               |
| **Type**  | Human-in-the-loop    |
| **Focus** | Interactive Sessions |

## Description

The User therapist is a special agent type that delegates therapeutic responses to a human operator. This enables interactive training scenarios, human evaluation studies, and live demonstrations where a real person provides the therapeutic interventions while interacting with simulated clients.

## Key Features

- **Real-time interaction** - Human provides responses in real-time
- **Full control** - Complete flexibility in therapeutic approach
- **Training mode** - Ideal for student therapist practice
- **Evaluation studies** - Enables human evaluation of client agents

## Configuration

### YAML Configuration

```yaml
therapist:
  agent_type: user
```

### Python Usage

```python
from omegaconf import OmegaConf

from patienthub.therapists import get_therapist

config = OmegaConf.create({"agent_type": "user"})
therapist = get_therapist(configs=config, lang="en")
```

## Parameters

The User therapist does not require additional configuration parameters as it relies on human input.

## Use Cases

- Training scenarios for mental health students
- Human evaluation studies of client agents
- Interactive demonstrations and presentations
- Research comparing human vs. AI therapist responses
- Quality assurance testing of client simulations

## Integration

The User therapist integrates with PatientHub's interactive interfaces:

- **Chainlit Web Demo** - Provides a chat interface for human interaction
- **Command Line** - Text-based interaction through the terminal
- **Custom Interfaces** - Can be integrated with custom UIs
