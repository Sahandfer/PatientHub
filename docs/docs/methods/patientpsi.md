---
sidebar_position: 2
---

# PatientPsi

> PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals

**Venue**: EMNLP 2024 (Main Conference)  
**Paper**: [ACL Anthology](https://aclanthology.org/2024.emnlp-main.711/)

## Overview

PatientPsi creates realistic patient simulations based on cognitive behavioral therapy (CBT) principles. It models patients with specific cognitive distortions, core beliefs, and automatic thoughts.

## Key Features

- **Cognitive Model**: Implements CBT cognitive triangle (thoughts, feelings, behaviors)
- **Core Beliefs**: Persistent underlying beliefs that drive behavior
- **Automatic Thoughts**: Spontaneous negative thoughts triggered by situations
- **Personality Modeling**: Big Five personality traits influence responses

## Usage

### CLI

```bash
uv run python -m examples.simulate client=patientPsi therapist=CBT
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Dr. Smith'})

response = client.generate_response("How have you been feeling lately?")
print(response.content)
```

## Configuration

| Option         | Description            | Default                           |
| -------------- | ---------------------- | --------------------------------- |
| `data_path`    | Path to character file | `data/characters/PatientPsi.json` |
| `data_idx`     | Character index        | `0`                               |
| `patient_type` | Behavior pattern       | `"upset"`                         |

## Character Data Format

```json
{
  "demographics": {
    "name": "Alex",
    "age": 28,
    "gender": "male",
    "occupation": "software engineer"
  },
  "mental_state": {
    "affect": "depressed, anxious",
    "behavior": "social withdrawal, procrastination",
    "cognition": {
      "core_beliefs": ["I am inadequate", "Others are more competent than me"],
      "negative_automatic_thoughts": [
        "I will fail this project",
        "Everyone will see I'm a fraud"
      ]
    }
  },
  "personality": {
    "summary": "Introverted, perfectionistic, self-critical",
    "openness": 6,
    "conscientiousness": 8,
    "extraversion": 3,
    "agreeableness": 7,
    "neuroticism": 8
  },
  "presenting_problem": "Experiencing anxiety and depression related to work performance"
}
```

## How It Works

1. **System Prompt Construction**: Combines demographic info, cognitive model, and personality
2. **Response Generation**: Patient responds based on core beliefs and automatic thoughts
3. **Consistency**: Maintains character consistency through conversation history

### Cognitive Triangle

```
        Thoughts
       (Automatic)
           │
     ┌─────┴─────┐
     ▼           ▼
 Feelings ◄───► Behaviors
 (Affect)     (Actions)
```

## Example Conversation

**Therapist**: "How have you been feeling at work lately?"

**Patient (PatientPsi)**: "Honestly, not great. I've been really anxious about the new project. Every time I sit down to work on it, I keep thinking that I'm going to mess it up somehow. Like everyone else on the team seems to know what they're doing, but I feel like I'm just... pretending."

**Therapist**: "It sounds like you're experiencing some self-doubt. Can you tell me more about these thoughts?"

**Patient**: "I guess... I just feel like I'm not as good as everyone thinks I am. Like eventually they're going to figure out that I don't really belong here. I've been avoiding meetings because I'm afraid someone will ask me a question and I won't know the answer."

## Best Practices

1. **Use with CBT Therapist**: Designed for CBT-style interactions
2. **Explore Automatic Thoughts**: Ask about specific situations to trigger cognitive patterns
3. **Note Avoidance Behaviors**: Character will demonstrate behavioral symptoms

## Limitations

- Single-session focus (no memory between sessions)
- Fixed cognitive model (doesn't update based on therapy)
- Best suited for CBT training scenarios

## Related Methods

- [ConsistentMI](/docs/methods/consistentmi) - For MI-focused training
- [Eeyore](/docs/methods/eeyore) - For depression-specific simulation
