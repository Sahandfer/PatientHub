# CARS

> When Clients Stop Following: A Cognitive Conceptualization Diagram-driven Framework for Strategic Counseling

**Paper**: [arXiv](https://arxiv.org/abs/2606.04389)

Expands a Cognitive Conceptualization Diagram (CCD) and a few seed statements into a full CARS client profile — a persona plus a session-specific cognitive/resistance pattern — following the paper's diverse-profile generation (§3.1.3).

## Overview

| Property   | Value                |
| ---------- | -------------------- |
| **Key**    | `cars`               |
| **Type**   | LLM-based            |
| **Output** | CARS character files |

## Key Features

- **Persona generation**: From a main CCD and seed sentences, produces demographics, family background, interpersonal relationships, physical condition, lifestyle, and chief complaint.
- **Session cognitive-pattern generation**: From the persona, CCD, and a dialogue excerpt, produces the counseling background, a session-specific CCD (automatic thought, intermediate belief, resistance triggers), preferred counselor style, and other client characteristics.
- **Diverse profiles**: Different seeds yield distinct cognitive patterns and resistance triggers, matching the paper's goal of a varied evaluation set.

## How It Works

`generate_character(seed)` runs two sequential LLM stages and assembles the result:

1. **Persona** — `generate_persona(main_ccd, sentences)` produces a persona (name, age, gender, occupation, family background, interpersonal relationships, physical condition, lifestyle, chief complaint).
2. **Cognitive patterns** — `generate_cognitive_patterns(persona, main_ccd, dialogue_excerpt)` produces the background, session-specific CCD, preferences, and client characteristics.
3. **Assemble** — combines the persona, the passed-in `main_ccd`, and the generated patterns into a `CarsCharacter`.

The character is returned; the `generate` CLI owns all I/O (loading seeds, saving output).

## Usage

Provide seeds as a JSON list and run the CLI:

```bash
patienthub generate generator=cars input_path=data/seeds/cars.json
```

A single **illustrative** seed ships at `data/seeds/cars.json` so the generator is runnable out of the box. It is authored for PatientHub, **not** from the CARS paper or any released dataset. To reproduce the paper's diverse-profile generation, replace `main_ccd` with entries from a CBT-grounded CCD library and `mesc_sentences` with statements sampled from MESC (Chu et al., 2025).

## Configuration

| Parameter     | Type   | Default                            | Description          |
| ------------- | ------ | ---------------------------------- | -------------------- |
| `agent_name`  | string | `cars`                             | Generator identifier |
| `prompt_path` | string | `data/prompts/generator/cars.yaml` | Path to prompt file  |
| `model_type`  | string | `"OPENAI"`                         | Model provider key   |
| `model_name`  | string | `"gpt-4o"`                         | Model identifier     |
| `temperature` | float  | `0.7`                              | Sampling temperature |
| `max_tokens`  | int    | `8192`                             | Max response tokens  |
| `max_retries` | int    | `3`                                | API retry attempts   |

## Seed Record Format

Seeds live in `data/seeds/cars.json` as a JSON list. Each record is validated against
`CarsSeed` before generation — one character is produced per record:

```json
[
  {
    "main_ccd": {
      "name": "Alex",
      "relevant_history": "Grew up with a highly critical parent ...",
      "core_beliefs": ["I am trapped.", "I am a failure."],
      "intermediate_beliefs": [
        "If I set a goal and fail, it proves I am incompetent."
      ],
      "coping_strategies": ["Avoidance of goal-setting and commitment."]
    },
    "mesc_sentences": [
      "I've tried making plans before and they never stick.",
      "Honestly, I don't really see the point in setting goals.",
      "Whenever I fail at something, it just confirms what I already think about myself."
    ],
    "dialogue_excerpt": [
      {
        "role": "Therapist",
        "content": "Could we look at one small goal together?"
      },
      {
        "role": "Client",
        "content": "Goals? I don't think they work. I always fail."
      }
    ]
  }
]
```

| Field              | Type   | Description                                                   |
| ------------------ | ------ | ------------------------------------------------------------- |
| `main_ccd`         | object | A CBT-grounded main CCD (beliefs, history, coping strategies) |
| `mesc_sentences`   | list   | At least **three** sampled counseling statements (MESC-style) |
| `dialogue_excerpt` | list   | Counselor–client turns, each `{ "role", "content" }`          |

## Output Format

```json
{
  "name": "Alex",
  "persona": {
    "name": "Alex",
    "age": "23 years old",
    "gender": "Male",
    "occupation": "Unemployed",
    "family_background": "...",
    "interpersonal_relationships": "...",
    "physical_condition": "...",
    "lifestyle": "...",
    "chief_complaint": "..."
  },
  "background": "The current counseling topic is treatment goal setting ...",
  "main_ccd": {
    "name": "Alex",
    "relevant_history": "...",
    "core_beliefs": ["..."],
    "intermediate_beliefs": ["..."],
    "coping_strategies": ["..."]
  },
  "session_ccd": {
    "theme": "goal setting",
    "structured_cbt_strategy": "Goal list or agenda setting",
    "automatic_thought": {
      "situation": "...",
      "cognition": "...",
      "reaction": "..."
    },
    "intermediate_belief": {
      "attitude": "...",
      "rule": "...",
      "assumption": "..."
    },
    "resistance_triggers": ["..."]
  },
  "preferences": { "positive": ["..."], "negative": ["..."] },
  "client_characteristics": {
    "possible_responses_under_different_emotions": ["..."],
    "other_client_characteristics": ["..."]
  }
}
```

## Note on the Emotion-Utterance Corpus

The paper references a _"pre-defined emotion-utterance corpus"_ (§3.1.2) used at response time. The authors do not publish it, so the generator does **not** produce one and CARS characters do not carry emotion-utterance examples. See the [CARS client](../clients/cars.md#emotion-utterance-corpus) for details.
