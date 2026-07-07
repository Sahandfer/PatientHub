# AnnaAgent

Creates character files for the AnnaAgent client, supporting multi-session counseling simulations with dynamic memory and clinical scale tracking.

## Overview

| Property   | Value                     |
| ---------- | ------------------------- |
| **Key**    | `annaAgent`               |
| **Type**   | LLM-based                 |
| **Output** | AnnaAgent character files |

## Key Features

- **Scale-based profiling**: Fills BDI, GHQ, and SASS scales for both previous and current treatment states
- **Age-appropriate event triggering**: Selects triggering life events from curated adult/teen event databases
- **Complaint chain generation**: Produces a 3–7 stage cognitive change chain from the triggering event
- **Speaking style inference**: Extracts the patient's speaking style from prior conversation history
- **Status summarization**: Analyzes scale changes across sessions to produce a current psychological status summary

## How It Works

`generate_character(seed)` runs the following pipeline:

1. Fill previous-session BDI, GHQ, and SASS scales from the seed case report
2. Select a triggering life event (age-matched within ±5 years; teens and seniors handled separately) from `events.json`
3. Generate a complaint cognitive change chain (3–7 stages)
4. Generate current situation, speaking style, and representative statements
5. Fill current-session BDI, GHQ, and SASS scales
6. Analyze scale changes and summarize the patient's current status

The resulting character is returned; the `generate` CLI saves it. Event databases
and scales are shared resources loaded from `resource_dir`.

## Usage

Provide seeds as a JSON list at `data/seeds/annaAgent.json` and run the CLI:

```bash
patienthub generate generator=annaAgent input_path=data/seeds/annaAgent.json
```

Each character is written to `data/characters/annaAgent.json` (override with `output_path`).

## Configuration

| Parameter      | Type   | Default                                 | Description                                            |
| -------------- | ------ | --------------------------------------- | ------------------------------------------------------ |
| `agent_name`   | string | `annaAgent`                             | Generator identifier                                   |
| `prompt_path`  | string | `data/prompts/generator/annaAgent.yaml` | Path to prompt file                                    |
| `events_path`  | string | `data/resources/annaAgent_events.json`  | Triggering-event database (by language + age group); clinical scales come from `patienthub.resources` |
| `model_type`   | string | `"OPENAI"`                              | Model provider key                                     |
| `model_name`   | string | `"gpt-4o"`                              | Model identifier                                       |
| `temperature`  | float  | `0.7`                                   | Sampling temperature                                   |
| `max_tokens`   | int    | `8192`                                  | Max response tokens                                    |
| `max_retries`  | int    | `3`                                     | API retry attempts                                     |

## Seed Record Format

Seeds live in `data/seeds/annaAgent.json` as a JSON list. Each record is validated
against `AnnaAgentSeed` before generation:

```json
[
  {
    "profile": {
      "name": "...",
      "age": 30,
      "gender": "Female"
    },
    "report": "...",
    "previous_conversations": [
      { "role": "Therapist", "content": "..." },
      { "role": "Client", "content": "..." }
    ]
  }
]
```

| Field                    | Type       | Description                                          |
| ------------------------ | ---------- | ---------------------------------------------------- |
| `profile`                | dict       | Case profile fields                                  |
| `report`                 | dict/str   | Prior-session case report (defaults to empty string) |
| `previous_conversations` | list       | Prior-session turns, each `{ "role", "content" }`    |

## Output Format

```json
{
  "profile": { "name": "...", "age": 30 },
  "situation": "Second-person description of current situation",
  "statement": ["Representative utterance 1", "Representative utterance 2"],
  "style": ["Speaking style trait 1", "Speaking style trait 2"],
  "complaint_chain": [
    {"stage": 1, "content": "..."},
    {"stage": 2, "content": "..."}
  ],
  "status": "Summary of current psychological status",
  "report": "Previous session psychological report",
  "previous_conversations": [...]
}
```

## Use Cases

- Creating character files for AnnaAgent multi-session simulations
- Building longitudinal therapy research datasets
