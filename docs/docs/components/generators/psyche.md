# Psyche Generator

> A Multi-faceted Patient Simulation Framework for Evaluation of Psychiatric Assessment Conversational Agents

**Paper**: [arXiv](https://arxiv.org/pdf/2501.01594)

Generates comprehensive MFC (Multi-Faceted Case) psychiatric profiles for use with the Psyche client agent.

## Overview

| Property   | Value                      |
| ---------- | -------------------------- |
| **Key**    | `psyche`                   |
| **Type**   | LLM-based                  |
| **Output** | Psyche MFC character files |

## Key Features

- **MFC-Profile**: Structured clinical intake — demographics, chief complaint, present illness, psychiatric/medical history, medication, family history, and risk assessment
- **MFC-History**: First-person biography-style life narrative grounded in the profile
- **MFC-Behavior**: Mental Status Examination — appearance, mood, affect, thought process, insight, and more

## How It Works

`generate_character()` runs three sequential LLM calls:

1. **MFC-Profile** — generates structured clinical data from a seed `input_dir` JSON (diagnosis, age, sex)
2. **MFC-History** — generates a first-person life narrative grounded in the profile
3. **MFC-Behavior** — generates a Mental Status Examination based on profile and history

The combined MFC object is saved to `output_dir`.

## Usage

```python
from patienthub.generators import get_generator

generator = get_generator(agent_name="psyche", lang="en")
generator.generate_character()
```

## Configuration

| Parameter     | Type   | Default                                | Description                                    |
| ------------- | ------ | -------------------------------------- | ---------------------------------------------- |
| `prompt_path` | string | `data/prompts/generator/psyche.yaml`   | Path to prompt file                            |
| `input_dir`   | string | `data/resources/psyche_character.json` | Path to seed JSON (diagnosis, age, sex)        |
| `output_dir`  | string | `data/characters/Psyche MFC.json`      | Path where the generated character is saved    |
| `model_type`  | string | `"OPENAI"`                             | Model provider key                             |
| `model_name`  | string | `"gpt-4o"`                             | Model identifier                               |
| `temperature` | float  | `0.7`                                  | Sampling temperature                           |
| `max_tokens`  | int    | `8192`                                 | Max response tokens                            |
| `max_retries` | int    | `3`                                    | API retry attempts                             |

## Input Data Format

```json
{
  "diagnosis": "Major Depressive Disorder",
  "age": "40",
  "sex": "Female"
}
```

## Output Format

```json
{
  "MFC-Profile": {
    "Identifying data": {"Age": "40", "Sex": "Female", "Marital status": "Married", "Occupation": "Office worker"},
    "Chief complaint": {"Description": "I feel overwhelmingly sad and have no energy."},
    "Present illness": {"Symptom": {"Name": "Persistent sadness", "Length": 24, "Stressor": "work"}},
    "Past psychiatric history": {"Presence": "No", "Description": null},
    "Impulsivity": {"Suicidal ideation": "High", "Suicidal plan": "Presence", "Homicide risk": "Low"}
  },
  "MFC-History": "I grew up in a small town...",
  "MFC-Behavior": {
    "Mood": "Depressed",
    "Affect": "Restricted, anxious, slightly tense",
    "Verbal productivity": "Decreased",
    "Thought process": "Normal"
  }
}
```

## Use Cases

- Creating character files for Psyche client agent simulations
- Psychiatric assessment training datasets
- Evaluating clinical interview agents
