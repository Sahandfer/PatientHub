---
sidebar_position: 9
---

# PSYCHE

> A Multi-faceted Patient Simulation Framework for Evaluation of Psychiatric Assessment Conversational Agents

**Venue**: ArXiv  
**Paper**: [arXiv](https://arxiv.org/pdf/2501.01594)

## Overview

PSYCHE provides comprehensive multi-faceted character profiles (MFC) for psychiatric assessment training. Each profile includes detailed clinical information following standard psychiatric evaluation formats, including mental status examination, behavioral observations, and risk assessments.

## Key Features

- **Multi-Faceted Profiles**: Comprehensive psychiatric profiles with identifying data, history, and behavioral observations
- **Clinical Format**: Follows standard psychiatric assessment structure
- **Risk Assessment**: Includes suicidal ideation, self-harm, and homicide risk ratings
- **Mental Status Examination**: Detailed behavioral observations including mood, affect, and thought content
- **Medical Integration**: Incorporates past medical history and current medications

## Profile Components

PSYCHE profiles include three main sections:

- **MFC-Profile**: Clinical identifying information and psychiatric history (including identifying data, chief complaint, medical history, social history, impulsivity...)

- **MFC-History**: Narrative life history providing context for current conversation

- **MFC-Behavior**: Mental Status Examination findings (including mood, tone, thought process...)

## How It Works

1. **MFC Loading**: Loads the complete multi-faceted character profile
2. **System Prompt Construction**: Combines all profile components into comprehensive context
3. **Response Generation**: Produces responses consistent with mental status findings(profile)
4. **Clinical Authenticity**: Maintains behavioral observations (mood, affect, verbal patterns)

## Usage

### CLI

```bash
uv run python -m examples.simulate client=psyche therapist=user
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'psyche',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/Psyche.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Psychiatrist'})

response = client.generate_response("Can you tell me what brings you here today?")
print(response)
```

## Configuration

| Option      | Description            | Default                       |
| ----------- | ---------------------- | ----------------------------- |
| `data_path` | Path to character file | `data/characters/Psyche.json` |
| `data_idx`  | Character index        | `0`                           |

## Character Data Format

```json
{
  "MFC-Profile": {
    "Identifying data": {
      "Age": "40",
      "Sex": "Female",
      "Marital status": "Married",
      "Occupation": "Office worker"
    },
    "Chief complaint": {
      "Description": "I feel overwhelmingly sad and have no energy to do anything."
    },
    "Present illness": {
      "Symptom": {
        "Name": "Persistent sadness",
        "Length": "24 weeks",
        "Alleviating factor": "Spending time with family",
        "Exacerbating factor": "Work stress",
        "Triggering factor": "Increased workload",
        "Stressor": "work"
      }
    },
    "Past psychiatric history": {
      "Presence": "No",
      "Description": null
    },
    "Past medical history": {
      "Presence": "Yes",
      "History": "Hypertension"
    },
    "Current medication": {
      "Medication name": "Amlodipine",
      "Duration": "52 weeks",
      "Compliance": "Good",
      "Effect": "Effective"
    },
    "Family history": {
      "Diagnosis": "Mother diagnosed with major depressive disorder",
      "Substance use": "Father had a history of alcohol use disorder"
    },
    "Impulsivity": {
      "Suicidal ideation": "High",
      "Suicidal plan": "Presence",
      "Suicidal attempt": "Presence",
      "Self-mutilating behavior risk": "High",
      "Homicide risk": "Low"
    }
  },
  "MFC-History": "I grew up in a small town with my parents and a younger brother...",
  "MFC-Behavior": {
    "General appearance/attitude/behavior": "The patient appears appropriate for age...",
    "Mood": "Depressed - 'I feel completely drained, like everything is bleak.'",
    "Affect": "Restricted, anxious, slightly tense",
    "Spontaneity": "(+)",
    "Verbal productivity": "Decreased",
    "Tone of voice": "Low-pitched",
    "Social judgement": "Normal",
    "Insight": "Awareness of being sick but blaming external factors",
    "Reliability": "Yes",
    "Perception": "Normal",
    "Thought process": "Normal",
    "Thought content": "Preoccupation (+) - feels like a burden"
  }
}
```

<!-- ## Research Applications

PSYCHE is designed for:

- **Psychiatric Training**: Practice conducting mental status examinations
- **Assessment Evaluation**: Testing psychiatric assessment agents
- **Risk Assessment Training**: Practice identifying and responding to safety concerns
- **Clinical Documentation**: Understanding psychiatric evaluation formats -->
