# ClientCast Generator

> Towards a Client-Centered Assessment of LLM Therapists by Client Simulation

**Paper**: [arXiv](https://arxiv.org/pdf/2406.12266)

Extracts a structured psychological profile from a real therapy conversation, including Big Five personality traits and PHQ-9 / GAD-7 / OQ-45 symptom estimates.

## Overview

| Property   | Value                      |
| ---------- | -------------------------- |
| **Key**    | `clientCast`               |
| **Type**   | LLM-based                  |
| **Output** | ClientCast character files |

## Key Features

- **Basic profile extraction**: Infers demographics, presenting problem, emotional style, and resistance level from conversation text
- **Big Five personality traits**: Estimates Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism with percentage scores
- **Clinical scale estimation**: Scores PHQ-9, GAD-7, and OQ-45 items from the conversation

## How It Works

`generate_character()` runs three sequential LLM calls:

1. **Basic profile** — extracts name, gender, age, occupation, topic, situation, emotion, resistance, and emotional fluctuation
2. **Big Five** — estimates each trait as a percentage score with explanation
3. **Symptoms** — scores individual items from PHQ-9, GAD-7, and OQ-45

The result is saved to `output_dir`.

## Usage

```python
from patienthub.generators import get_generator

generator = get_generator(agent_name="clientCast", lang="en")
generator.generate_character()
```

## Configuration

| Parameter      | Type   | Default                                       | Description                                      |
| -------------- | ------ | --------------------------------------------- | ------------------------------------------------ |
| `prompt_path`  | string | `data/prompts/generator/clientCast.yaml`      | Path to prompt file                              |
| `input_dir`    | string | `data/resources/ClientCast/human_data.json`   | Path to input conversation JSON                  |
| `symptoms_dir` | string | `data/resources/ClientCast/symptoms.json`     | Path to symptom item definitions                 |
| `output_dir`   | string | `data/characters/ClientCast.json`             | Path where the generated character is saved      |
| `data_idx`     | int    | `0`                                           | Index of the conversation to use from input file |
| `model_type`   | string | `"OPENAI"`                                    | Model provider key                               |
| `model_name`   | string | `"gpt-4o"`                                    | Model identifier                                 |
| `temperature`  | float  | `0.7`                                         | Sampling temperature                             |
| `max_tokens`   | int    | `8192`                                        | Max response tokens                              |
| `max_retries`  | int    | `3`                                           | API retry attempts                               |

## Input Data Format

The input file is a JSON array of conversation objects:

```json
[
  {
    "messages": [
      {"role": "Therapist", "content": "What brings you here today?"},
      {"role": "Client", "content": "I've been feeling really low lately..."}
    ]
  }
]
```

`data_idx` selects which conversation to process.

## Output Format

```json
{
  "basic_profile": {
    "name": "Not Specified",
    "gender": "Female",
    "age": 34,
    "occupation": "Teacher",
    "topic": "smoking cessation – wants to quit but struggles with cravings.",
    "situation": "The client feels overwhelmed by work stress and persistent low mood.",
    "emotion": "The client feels anxious and guilty about disappointing others.",
    "resistance": "Low – the client is open to suggestions."
  },
  "big_five": {
    "Openness": {"score_percent": 62, "explanation": "..."},
    "Conscientiousness": {"score_percent": 55, "explanation": "..."}
  },
  "symptoms": {
    "PHQ9": {"1": {"identified": true, "severity_level": 2, "severity_label": "More than half the days", "explanation": "..."}},
    "GAD7": {"1": {"identified": true, "severity_level": 1, "explanation": "..."}},
    "OQ45": {"1": {"identified": false, "explanation": "..."}}
  }
}
```

## Use Cases

- Creating ClientCast character files from existing therapy transcripts
- Building assessment datasets from real or simulated conversations
