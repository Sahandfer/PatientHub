---
sidebar_position: 6
---

# SimPatient

> Scaffolding Empathy: Training Counselors with Simulated Patients and Utterance-level Performance Visualizations

**Venue**: CHI 2025  
**Paper**: [ACM DL](https://dl.acm.org/doi/full/10.1145/3706598.3714014)

## Overview

SimPatient models patients dealing with alcohol misuse using a cognitive model that tracks internal states. The patient's responses evolve based on the therapist's approach, with a unique feature of generating between-session events that reflect real-world patient experiences between appointments.

## Key Features

- **Cognitive Model**: Tracks 4 internal states (control, efficacy, awareness, reward) on 1-10 scales
- **Dynamic State Updates**: Internal states evolve based on therapist interactions
- **Between-Session Events**: Generates realistic events that occur between therapy sessions
- **Session Continuity**: Can continue from previous session state and history
- **Motivational Interviewing Focus**: Designed for MI-based counseling training

## How It Works

1. **Profile Loading**: Loads patient persona and initial cognitive model state
2. **Session Initialization**: Optionally continues from previous session with updated states
3. **Response Generation**: Generates responses based on current cognitive model
4. **State Update**: After each interaction, updates the four cognitive dimensions
5. **Between-Session Generation**: Creates realistic events for multi-session continuity

## Cognitive Model

SimPatient tracks four dimensions of patient psychology:

| Dimension           | Description                                    | Scale |
| ------------------- | ---------------------------------------------- | ----- |
| `patient_control`   | Perceived control over drinking behavior       | 1-10  |
| `patient_efficacy`  | Self-efficacy for making changes               | 1-10  |
| `patient_awareness` | Awareness of the problem and its consequences  | 1-10  |
| `patient_reward`    | Perceived reward/benefit from current behavior | 1-10  |

## Usage

### CLI

```bash
# New session
uv run python -m examples.simulate client=simPatient therapist=MI

# Continue from previous session
uv run python -m examples.simulate client=simPatient client.continue_last_session=true
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'simPatient',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/SimPatient.json',
    'data_idx': 0,
    'continue_last_session': False,
    'conv_history_path': 'data/sessions/SimPatient/session_1.json',
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Counselor'})

response = client.generate_response("How have things been going since we last talked?")
print(response)
```

## Configuration

| Option                  | Description                      | Default                                   |
| ----------------------- | -------------------------------- | ----------------------------------------- |
| `data_path`             | Path to character file           | `data/characters/SimPatient.json`         |
| `data_idx`              | Character index                  | `0`                                       |
| `continue_last_session` | Resume from previous session     | `False`                                   |
| `conv_history_path`     | Path to previous session history | `data/sessions/SimPatient/session_1.json` |

## Character Data Format

```json
{
  "persona": {
    "age": 34,
    "gender": "male",
    "ethnicity": "Asian",
    "occupation": "software engineer",
    "mbti": "INTJ-A"
  },
  "cognitive_model": {
    "patient_control": 3,
    "patient_efficacy": 4,
    "patient_awareness": 7,
    "patient_reward": 8
  },
  "between_session_event": "After a stressful day at work, the patient received a call from a college friend inviting him to a small get-together..."
}
```

## Between-Session Events

SimPatient can generate realistic between-session events:

```python
# The system automatically generates events like:
"After a stressful day at work, the patient received a call from
a college friend inviting him to a small get-together. He hesitated
but decided to go, thinking he could handle it. However, once there,
the sight and smell of alcohol triggered his cravings..."
```

## State Update Example

After a therapist message about coping strategies:

```python
# Before interaction
cognitive_model = {
    "patient_control": 3,
    "patient_efficacy": 4,
    "patient_awareness": 7,
    "patient_reward": 8
}

# After positive therapeutic interaction
cognitive_model = {
    "patient_control": 4,  # Slight improvement
    "patient_efficacy": 5, # Increased confidence
    "patient_awareness": 8, # Better understanding
    "patient_reward": 7    # Reduced perceived reward from drinking
}
```
