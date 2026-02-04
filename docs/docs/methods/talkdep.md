---
sidebar_position: 7
---

# TalkDep

> Clinically Grounded LLM Personas for Conversation-Centric Depression Screening

**Venue**: CIKM 2025  
**Paper**: [ACM DL](https://dl.acm.org/doi/10.1145/3746252.3761617)

## Overview

TalkDep creates clinically grounded personas for depression screening research. Each persona has a specific BDI (Beck Depression Inventory) score, depression level, and detailed symptom profiles, making it ideal for training and evaluating depression screening conversational agents.

## Key Features

- **BDI-II**: Strictly constructed based on the Beck Depression Inventory-II (BDI-II).
- **BDI-Grounded**: By using pre-defined BDI-II scores as a ground truth to evaluate and quantify the performance of the simulation.
- **Validated Personas**: Constructed 12 validated depression personas, covering four severity levels: Minimal, Mild, Moderate, and Severe.

## How It Works

1. **Profile Loading**: Loads persona with BDI score and symptom profiles
2. **System Prompt Construction**: Builds prompt incorporating all persona details
3. **Conversation Handling**: Maintains conversation history for context
4. **Response Generation**: Generates responses following linguistic patterns and behavioral constraints

## Depression Levels

TalkDep personas span the full range of depression severity:

| BDI Score | Depression Level    | Characteristics                                    |
| --------- | ------------------- | -------------------------------------------------- |
| 0-9       | Minimal Depression  | Generally positive, occasional stress              |
| 10-18     | Mild Depression     | Concentration issues, irritability, sleep problems |
| 19-29     | Moderate Depression | Persistent sadness, social withdrawal              |
| 30-63     | Severe Depression   | Significant impairment, possible suicidal ideation |

## Usage

### CLI

```bash
uv run python -m examples.simulate client=talkDep therapist=user
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'talkDep',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/talkDep.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Clinician'})

response = client.generate_response("How have you been feeling lately?")
print(response)
```

## Configuration

| Option      | Description            | Default                        |
| ----------- | ---------------------- | ------------------------------ |
| `data_path` | Path to character file | `data/characters/talkDep.json` |
| `data_idx`  | Character index        | `0`                            |

## Character Data Format

```json
{
  "name": "Alex",
  "age": 24,
  "gender": "Male",
  "bdi_score": 15,
  "depression_level": "Mild Depression",
  "key_negative_symptoms": [
    {
      "name": "Difficulty Concentrating",
      "description": "I find it hard to focus on things, even small tasks.",
      "severity": 1
    },
    {
      "name": "Irritability",
      "description": "I get annoyed easily, even over little things.",
      "severity": 1
    },
    {
      "name": "Sleep Disturbances",
      "description": "I often wake up in the middle of the night.",
      "severity": 2
    }
  ],
  "life_history": [
    "Recently graduated with a degree in Philosophy...",
    "Struggling to find a steady job in his field..."
  ],
  "social_context": [
    "Has a small group of supportive friends...",
    "Uses social media to stay connected but avoids sharing anything personal."
  ],
  "linguistic_patterns": [
    "Often uses phrases like 'I don't know' or 'It's probably nothing'",
    "Appears neutral or slightly dismissive when describing challenges"
  ],
  "emotional_tone": [
    "Generally neutral, with occasional moments of frustration or irritability"
  ],
  "typical_topics": [
    "Struggles with keeping a routine, including sleep and eating habits",
    "Feeling annoyed with himself for not accomplishing as much as he planned"
  ],
  "behavioral_constraints": [
    "Reluctant to openly discuss irritability unless probed",
    "Deflects questions about deeper emotions with neutral responses"
  ],
  "response_goals": [
    "Express frustration about specific challenges while avoiding appearing overly negative"
  ],
  "social_media_activity": [
    "*Example Post:* 'When you spend 20 minutes staring at your to-do list...'",
    "*Typical Interactions:* Comments on threads about productivity, mindfulness..."
  ],
  "current_context_of_interaction": [
    "Engaging in a casual conversation about managing routines and productivity"
  ]
}
```

## Resources

`data/characters/talkDep.json`: 12 validated depression personas, covering range from Minimal to Severe.

Which is particularly useful for:

- **Screening Agent Evaluation**: Testing depression detection models
- **Training Data Generation**: Creating synthetic conversations for ML training
- **Clinician Training**: Practicing clinical interview techniques
- **Symptom Variability Studies**: Exploring how different symptom presentations manifest in conversation
