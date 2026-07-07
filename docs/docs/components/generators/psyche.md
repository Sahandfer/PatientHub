# Psyche

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

`generate_character(seed)` runs three sequential LLM calls:

1. **MFC-Profile** — generates structured clinical data from the seed record (diagnosis, age, sex)
2. **MFC-History** — generates a first-person life narrative grounded in the profile
3. **MFC-Behavior** — generates a Mental Status Examination based on profile and history

The combined MFC object is returned; the `generate` CLI saves it.

## Usage

Provide seeds as a JSON list at `data/seeds/psyche.json` and run the CLI:

```bash
patienthub generate generator=psyche input_path=data/seeds/psyche.json
```

Each character is written to `data/characters/psyche.json` (override with `output_path`).

## Configuration

| Parameter     | Type   | Default                              | Description          |
| ------------- | ------ | ------------------------------------ | -------------------- |
| `agent_name`  | string | `psyche`                             | Generator identifier |
| `prompt_path` | string | `data/prompts/generator/psyche.yaml` | Path to prompt file  |
| `model_type`  | string | `"OPENAI"`                           | Model provider key   |
| `model_name`  | string | `"gpt-4o"`                           | Model identifier     |
| `temperature` | float  | `0.7`                                | Sampling temperature |
| `max_tokens`  | int    | `8192`                               | Max response tokens  |
| `max_retries` | int    | `3`                                  | API retry attempts   |

## Seed Record Format

Seeds live in `data/seeds/psyche.json` as a JSON list. Each record is validated
against `PsycheSeed` before generation:

```json
[
  {
    "diagnosis": "Major Depressive Disorder",
    "age": 40,
    "sex": "Female"
  }
]
```

| Field       | Type   | Description        |
| ----------- | ------ | ------------------ |
| `diagnosis` | string | Target diagnosis   |
| `age`       | int    | Patient age        |
| `sex`       | string | Patient sex        |

## Output Format

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
      "Description": "I feel overwhelmingly sad and have no energy."
    },
    "Present illness": {
      "Symptom": {
        "Name": "Persistent sadness",
        "Length": 24,
        "Stressor": "work"
      }
    },
    "Past psychiatric history": { "Presence": "No", "Description": null },
    "Impulsivity": {
      "Suicidal ideation": "High",
      "Suicidal plan": "Presence",
      "Homicide risk": "Low"
    }
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
