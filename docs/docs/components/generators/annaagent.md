# AnnaAgent Generator

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

`generate_character()` runs the following pipeline:

1. Fill previous-session BDI, GHQ, and SASS scales from the input case report
2. Select a triggering life event (age-matched from `adult_events.csv` / `teen_events.json`)
3. Generate a complaint cognitive change chain (3–7 stages)
4. Generate current situation, speaking style, and representative statements
5. Fill current-session BDI, GHQ, and SASS scales
6. Analyze scale changes and summarize the patient's current status
7. Save the resulting character JSON to `output_dir`

## Usage

```python
from patienthub.generators import get_generator

generator = get_generator(agent_name="annaAgent", lang="en")
generator.generate_character()
```

## Configuration

| Parameter     | Type   | Default                                 | Description                                   |
| ------------- | ------ | --------------------------------------- | --------------------------------------------- |
| `prompt_path` | string | `data/prompts/generator/annaAgent.yaml` | Path to prompt file                           |
| `input_dir`   | string | `data/resources/AnnaAgent`              | Directory with `case.json`, event files, etc. |
| `output_dir`  | string | `data/characters/AnnaAgent.json`        | Path where the generated character is saved   |
| `model_type`  | string | `"OPENAI"`                              | Model provider key                            |
| `model_name`  | string | `"gpt-4o"`                              | Model identifier                              |
| `temperature` | float  | `0.7`                                   | Sampling temperature                          |
| `max_tokens`  | int    | `8192`                                  | Max response tokens                           |
| `max_retries` | int    | `3`                                     | API retry attempts                            |

## Input Data Format

The generator reads from `input_dir/case.json`:

```json
{
  "profile": {
    "name": "...",
    "age": 30,
    "gender": "Female"
  },
  "report": "...",
  "previous_conversations": [
    {"role": "Therapist", "content": "..."},
    {"role": "Client", "content": "..."}
  ]
}
```

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
