---
sidebar_position: 13
---

# PatientAct

> Trust-Gated Disclosure and Behavior Planning for Psychotherapy Client Simulation

## Overview

PatientAct simulates a psychotherapy client who does not hand the therapist their whole case file. Every piece of the profile is stored as a **memory item** carrying a disclosure level — the minimum trust at which the client would say it out loud. Trust is not fixed: it moves up and down after every exchange based on how the therapist handled the client.

Two things therefore change turn by turn: **what** the client can access (only items at or below the current trust level are retrieved) and **how** the client responds (an emotional reaction, a conversational behavior, and — if that behavior is resistance — a specific resistance pattern, each decided before any text is generated). The therapist's approach, not just their questions, determines what the session surfaces.

## Key Features

- **Trust-gated memory**: Each memory item carries a disclosure level in `[1.0, 4.0]`; items above the current trust level do not enter the context.
- **Discomfort on blocked content**: An item that is gated *and* flagged `generates_discomfort` still signals that a sensitive topic was approached, producing visible avoidance rather than silence.
- **Explicit response pipeline**: Reaction, behavior, and resistance pattern are separate structured decisions made before the response text.
- **Dynamic trust**: A trust critic scores each exchange and shifts trust by up to ±0.5, clamped to `[1.0, 4.0]`.
- **Topic-based retrieval**: Memory items carry activation tags; the therapist's utterance is mapped onto those tags to decide what is relevant.
- **Ablation switches**: `use_memory`, `use_pipeline`, and `use_trust_gating` each disable one mechanism independently.

## How It Works

Each call to `generate_response()` runs six steps:

1. **Topic extraction**: the therapist's utterance is matched against all activation tags in the client's memory.
2. **Retrieval and trust gate**: items whose tags intersect the extracted topics are collected. An item is retrieved if `trust_level >= disclosure_level`; otherwise it is dropped, or added to `blocked` when flagged `generates_discomfort`.
3. **Reaction**: the client picks one of seven emotional reactions plus an intensity.
4. **Behavior**: the client picks one of eight conversational behaviors, informed by the reaction, recent behaviors, trust level, and whether anything was blocked.
5. **Resistance pattern**: only when the chosen behavior is `resistance`, one of seven specific patterns is selected.
6. **Response and trust update**: the retrieved context and planned signals are appended to the last therapist turn, the response is generated, and the trust critic updates `trust_level`.

## Trust and Disclosure

Trust starts at `2.5` — a neutral session opening — and is clamped to `[1.0, 4.0]`. After each exchange the trust critic reads the conversation, the client's attachment style, and the client's expected response from a therapist (the `the therapist` interpersonal pattern, when the profile has one), and returns a direction:

| Direction                 | Delta   |
| ------------------------- | ------- |
| `increased_significantly` | `+0.50` |
| `increased_slightly`      | `+0.25` |
| `unchanged`               | `0.00`  |
| `decreased_slightly`      | `-0.25` |
| `decreased_significantly` | `-0.50` |

Because disclosure levels are quantized to half-steps (`1.0, 1.5, … 4.0`), a single strongly positive exchange can unlock a new tier of material, and a single mishandled one can close it again.

Each memory item is built once at generation time and carries:

| Field                  | Meaning                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `field_path`           | Dotted path back into the profile, e.g. `psychological_formulation.triggers.0`                                            |
| `content`              | The disclosable text                                                                                                      |
| `disclosure_level`     | Minimum trust required: `1.0` active refusal, `2.0` hesitant, `2.5` session start, `3.0` building trust, `4.0` fully open |
| `activation_tags`      | 3–5 conversational topics that make this item relevant                                                                    |
| `generates_discomfort` | Whether gating this item produces visible discomfort, rather than the content simply not surfacing                        |

Retrieved items are prefixed by type — `[trigger]`, `[belief]`, `[thought]`, `[pattern]`, `[relational pattern]`, `[symptom]`, or `[memory]` — so the response prompt can treat them differently.

## Reactions, Behaviors, and Resistance

The three taxonomies live in `patienthub.schemas.patientAct`.

**Reactions** (`REACTIONS`) — positive: `understood`, `hopeful`, `gained_clarity`, `challenged`; negative: `scared`, `misunderstood`; neutral: `no_reaction`. Each is chosen with an intensity of `low`, `moderate`, or `high`.

**Behaviors** (`BEHAVIORS`) — `simple_response`, `request`, `recounting`, `cognitive_exploration`, `affective_exploration`, `insight`, `discussing_plans`, `resistance`.

**Resistance patterns** (`RESISTANCE_PATTERNS`), selected only when the behavior is `resistance`:

| Axis              | Patterns                                                      |
| ----------------- | ------------------------------------------------------------- |
| Response quantity | `minimal_talk`                                                |
| Response content  | `irrelevant_talk`, `superficial`, `intellectualizing`         |
| Response style    | `hostility`, `defensiveness`, `compliance_without_engagement` |

## Usage

### CLI

```bash
patienthub simulate client=patientAct
```

```bash
patienthub simulate client=patientAct client.use_trust_gating=false
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name="patientAct", lang="en")

response = client.generate_response("What feels hardest to talk about today?")
print(response.content)
print(client.trust_level, client.reaction, client.behavior)
```

## Configuration

| Option             | Description                                                                            | Default                               |
| ------------------ | -------------------------------------------------------------------------------------- | ------------------------------------- |
| `prompt_path`      | Path to prompt file                                                                    | `data/prompts/client/patientAct.yaml` |
| `data_path`        | Path to character file                                                                 | `data/characters/patientAct.json`     |
| `data_idx`         | Character index                                                                        | `0`                                   |
| `use_memory`       | Retrieve memory items; when `false`, the full profile sits in the system prompt instead | `true`                                |
| `use_pipeline`     | Plan reaction/behavior/resistance; when `false`, retrieved context is appended directly | `true`                                |
| `use_trust_gating` | Apply disclosure levels; when `false`, every topic-matched item is retrieved            | `true`                                |

The three switches are ablations, each isolating one mechanism. Turn off `use_trust_gating` to measure the pipeline's contribution alone; turn off `use_pipeline` to keep gated disclosure while the model chooses tone freely. With all three off, PatientAct degrades to a static profile role-play client. To make a case easier without touching the switches, lower the disclosure levels in its memory so more of the profile is reachable from the opening trust of `2.5`.

## Character Data Format

Each entry pairs a profile with its memory and the sampled seed that produced it. Profiles are produced by the [PatientAct generator](../generators/patientact.md).

```json
{
  "profile": {
    "demographics": {
      "name": "Alex Reyes",
      "gender": "male",
      "age_group": "Adult",
      "occupation": "Warehouse supervisor",
      "marital_status": "married",
      "cultural_background": "Filipino American"
    },
    "problem_formulation": {
      "presenting_problem": {
        "situation": "Referred after repeated medical visits for unexplained chest tightness.",
        "impact": ["Sleep disrupted most nights", "Avoids driving alone", "Missed four shifts this month"]
      },
      "precipitating_factors": ["A colleague's sudden heart attack"],
      "predisposing_factors": {
        "psychological": ["Learned early that expressing fear invited dismissal"],
        "social": ["Family treats illness as something to endure privately"]
      },
      "perpetuating_factors": {
        "internal": ["Scans body for symptoms hourly"],
        "external": ["Reassurance from relatives ends the conversation"]
      },
      "protective_factors": {
        "internal": ["Attends every appointment", "Wants to stay well for his children"],
        "external": ["Supportive spouse", "Stable employment"]
      }
    },
    "psychological_formulation": {
      "intermediate_beliefs": ["If I stop monitoring, I will miss the warning"],
      "automatic_thoughts": ["This time it is real"],
      "triggers": ["Discussing test results", "Chest sensations"],
      "coping_patterns": ["Seeks reassurance", "Rehearses worst cases"],
      "emotional_range": "Can name fear and irritation; shame stays out of reach.",
      "interpersonal_patterns": [
        {
          "domain": "the therapist",
          "wish": "To be taken seriously",
          "response_of_other": "Will decide he is exaggerating",
          "response_of_self": "Over-explains, then withdraws"
        }
      ]
    }
  },
  "memory": {
    "items": [
      {
        "field_path": "psychological_formulation.triggers.0",
        "content": "Discussing test results",
        "disclosure_level": 2.5,
        "activation_tags": ["medical tests", "doctors", "health worries"],
        "generates_discomfort": true
      }
    ]
  },
  "seed": {
    "gender": "male",
    "age_group": "Adult",
    "ethnicity": "Asian",
    "occupation_type": "Manual worker",
    "core_belief_theme": "I am helpless",
    "attachment_style": "anxious"
  },
  "situation": "The patient is preoccupied with the conviction that a serious physical illness is being missed ...",
  "disease_key": "anxiety_disorder"
}
```
