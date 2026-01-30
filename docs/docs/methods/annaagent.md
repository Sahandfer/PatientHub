---
sidebar_position: 4
---

# AnnaAgent 

> Dynamic Evolution Agent System with Multi-Session Memory for Realistic Seeker Simulation

**Venue**: ACL 2025 (Findings)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.findings-acl.1192/)

## Overview

AnnaAgent aims to simulate the dynamic evolution of the AI seeker's emotions and multi-session memory. It features a sophisticated emotion system based on the GoEmotions taxonomy (28 emotion categories) and models the progression of psychological complaints through multi-stage chains.

## Key Features

- **Multi-Session Memory**: Maintains context across multiple therapy sessions
- **Dynamic Evolution**: Complaint progression through cognitive change chains
- **28-Emotion System**: Based on GoEmotions taxonomy (Positive, Neutral, Ambiguous, Negative)
- **Profile-Based**: Detailed patient profiles with depression/suicide risk levels
- **Previous Session Integration**: References historical conversations when relevant

## Emotion Categories

AnnaAgent uses the GoEmotions taxonomy with weighted emotion transitions:

| Category  | Emotions                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------- |
| Positive  | admiration, amusement, approval, caring, curiosity, excitement, gratitude, joy, love, optimism, pride, relief |
| Neutral   | neutral                                                                                                       |
| Ambiguous | confusion, disappointment, nervousness                                                                        |
| Negative  | anger, annoyance, disapproval, disgust, embarrassment, fear, sadness, remorse, grief                          |

## Usage

### CLI

```bash
uv run python -m examples.simulate client=annaAgent therapist=CBT
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'annaAgent',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/AnnaAgent.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Dr. Kim'})

response = client.generate_response("How have you been since our last session?")
print(response.content)
```

## Configuration

| Option      | Description            | Default                          |
| ----------- | ---------------------- | -------------------------------- |
| `data_path` | Path to character file | `data/characters/AnnaAgent.json` |
| `data_idx`  | Character index        | `0`                              |

## Character Data Format

```json
{
  "profile": {
    "drisk": 3,
    "srisk": 2,
    "age": "42",
    "gender": "Female",
    "marital_status": "Divorced",
    "occupation": "Teacher",
    "symptoms": "Lack of self-confidence, low self-worth, feelings of guilt..."
  },
  "situation": "Description of the current situation triggering distress...",
  "statement": ["Initial statements the patient might make..."],
  "style": ["Self-critical", "Emotionally restrained", "Direct and concise"],
  "complaint_chain": [
    { "stage": 1, "content": "Initial complaint..." },
    { "stage": 2, "content": "Deeper realization..." },
    { "stage": 3, "content": "Core belief surfaces..." }
  ],
  "status": "Summary of patient's current mental health status...",
  "report": {
    "case_title": "...",
    "case_categories": ["Anxiety Disorder", "Low Self-Worth"],
    "techniques_used": ["Cognitive Behavioral Therapy", "Emotional Support"],
    "case_summary": ["..."],
    "counseling_process": ["..."],
    "insights_and_reflections": ["..."]
  },
  "previous_conversations": [
    { "role": "Client", "content": "..." },
    { "role": "Therapist", "content": "..." }
  ]
}
```

## How It Works

1. **Profile Loading**: Loads detailed patient profile with risk levels and symptoms
2. **Emotion Inference**: Determines emotional state based on therapist input
3. **Context Check**: Evaluates if historical information is needed for the response
4. **Complaint Progression**: Tracks progress through the cognitive change chain
5. **Response Generation**: Produces contextually appropriate responses with emotional consistency

## Resources

`data/resources/AnnaAgent/adult_events.csv`: Psychological distress events regarding adults
`data/resources/AnnaAgent/teen_events.json`: Psychological distress events regarding teenagers
`data/resources/AnnaAgent/scales.json`: Scales of GHQ, SASS and BDI

