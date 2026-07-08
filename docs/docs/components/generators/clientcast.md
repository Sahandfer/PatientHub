# ClientCast

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

`generate_character(seed)` runs three sequential LLM calls:

1. **Basic profile** — extracts name, gender, age, occupation, topic, situation, emotion, resistance, and emotional fluctuation
2. **Big Five** — estimates each trait as a percentage score with explanation
3. **Symptoms** — scores individual items from PHQ-9, GAD-7, and OQ-45

The result is returned; the `generate` CLI saves it.

## Usage

Provide seeds as a JSON list at `data/seeds/clientCast.json` and run the CLI:

```bash
patienthub generate generator=clientCast input_path=data/seeds/clientCast.json
```

Each conversation record produces one character, written to
`data/characters/clientCast.json` (override with `output_path`). Use `num_workers`
to process records in parallel and `resume=true` to refill only failed slots.

## Configuration

| Parameter       | Type   | Default                                   | Description                       |
| --------------- | ------ | ----------------------------------------- | --------------------------------- |
| `agent_name`    | string | `clientCast`                              | Generator identifier              |
| `prompt_path`   | string | `data/prompts/generator/clientCast.yaml`  | Path to prompt file               |
| `model_type`    | string | `"OPENAI"`                                | Model provider key                |
| `model_name`    | string | `"gpt-4o"`                                | Model identifier                  |
| `temperature`   | float  | `0.7`                                     | Sampling temperature              |
| `max_tokens`    | int    | `8192`                                    | Max response tokens               |
| `max_retries`   | int    | `3`                                       | API retry attempts                |

## Seed Record Format

Seeds live in `data/seeds/clientCast.json` as a JSON list. Each record is validated
against `ClientCastSeed` before generation — one character is produced per record:

```json
[
  {
    "conv_id": "conv_001",
    "messages": [
      { "role": "Therapist", "content": "What brings you here today?" },
      { "role": "Client", "content": "I've been feeling really low lately..." }
    ]
  }
]
```

| Field      | Type   | Description                                                |
| ---------- | ------ | --------------------------------------------------------- |
| `conv_id`  | string | Optional conversation identifier                          |
| `messages` | list   | Conversation turns, each `{ "role", "content" }`          |

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
    "Openness": { "score_percent": 62, "explanation": "..." },
    "Conscientiousness": { "score_percent": 55, "explanation": "..." }
  },
  "symptoms": {
    "PHQ-9": {
      "1": {
        "identified": true,
        "severity_level": 2,
        "severity_label": "More than half the days",
        "explanation": "..."
      }
    },
    "GAD-7": {
      "1": { "identified": true, "severity_level": 1, "explanation": "..." }
    },
    "OQ-45": { "1": { "identified": false, "explanation": "..." } }
  }
}
```

## Use Cases

- Creating ClientCast character files from existing therapy transcripts
- Building assessment datasets from real or simulated conversations
