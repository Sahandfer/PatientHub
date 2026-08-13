# PatientAct

> Trust-Gated Disclosure and Behavior Planning for Psychotherapy Client Simulation

Turns one clinical situation into one complete PatientAct client. It samples a demographic scaffold from disease-conditioned priors, builds the case formulation in stages, validates it against a disease outline, then derives the disclosure memory that gates what the client will say and when.

## Overview

| Property   | Value                         |
| ---------- | ----------------------------- |
| **Key**    | `patientAct`                  |
| **Type**   | LLM-based + sampled priors    |
| **Output** | PatientAct character files    |

## Key Features

- **Disease-conditioned priors**: Demographic attributes are sampled from global priors, overridden per disease where epidemiological data supports it.
- **Staged formulation**: Problem formulation, demographics, and psychological formulation are separate LLM calls, so each sees the previous output.
- **Deterministic conflict checks**: Regex rules catch scaffold/situation contradictions — a child with an office job, a male patient with postpartum evidence — before the model is asked to reconcile them.
- **Two-tier outlines**: Generation sees only key characteristics and typical presentation; validation additionally sees contraindications, differentials, and red flags.
- **Revision loops**: Demographics retry up to 5 times and the whole profile up to 3, each round carrying forward the specific issues found.
- **Separate memory pass**: The profile is what the client *is*; the memory is what the client *will say and when*.

## How It Works

`generate_character(seed)` runs six stages:

1. **Sample the scaffold** — `age_group`, `biological_sex`, `ethnicity`, `occupation_type`, `core_belief_theme`, and `attachment_style` are drawn by weighted choice from `attribute_priors.json`. Where `disease_priors.json` has an override for the record's `disease_key`, that distribution replaces the global one.
2. **Problem formulation** — the situation, disease outline, and scaffold *minus its psychological attributes* are given to the model. Core belief theme and attachment style are withheld here so the presenting problem is not written backwards from the intended psychology.
3. **Demographics** — `hard_conflict_issues()` scans the situation and problem formulation for contradictions with the scaffold, and any hits become revision guidance. If the model's `DemographicCompletionResult` does not pass, its own issues seed the next round, up to 5 attempts.
4. **Psychological formulation** — core belief theme and attachment style are now supplied, producing intermediate beliefs, automatic thoughts, triggers, coping patterns, emotional range, and interpersonal patterns.
5. **Validation** — the assembled profile is checked against the **full** disease outline, including the contraindications and red flags generation never saw. On failure, `revision_guidance` is threaded back into all three generation steps, up to 3 attempts.
6. **Memory** — `extract_memory_items()` deterministically collects the disclosable elements, then the model assigns each a disclosure level, activation tags, and a discomfort flag.

The deterministic conflict rules in stage 3 are:

| Scaffold             | Conflicting evidence                                                    |
| -------------------- | ----------------------------------------------------------------------- |
| `age_group: Child`   | Adult occupations; alcohol or adult-life language (married, coworker, …) |
| `age_group: Elderly` | `occupation_type: Student`; child or adolescent language                |
| `gender: male`       | Pregnancy, postpartum, or menopause language                            |

The `the therapist` interpersonal pattern is excluded from the memory: it drives the client's trust critic at simulation time, not disclosure.

The character is returned; the `generate` CLI owns all I/O (loading seeds, saving output).

## Usage

Provide seeds as a JSON list and run the CLI:

```bash
patienthub generate generator=patientAct input_path=data/seeds/patientAct.json
```

Resume a partial run — already-generated slots are kept, only `null` slots are filled:

```bash
patienthub generate generator=patientAct input_path=data/seeds/patientAct.json resume=true
```

Each worker builds its own generator, so parallel runs are safe:

```bash
patienthub generate generator=patientAct input_path=data/seeds/patientAct.json num_workers=4
```

`random_seed` defaults to `null` for a reason: one generator is built per input record, so a fixed integer seeds every record's RNG identically and the whole batch collapses onto a single demographic scaffold. Set it only when reproducing one record.

## Configuration

| Parameter       | Type   | Default                                  | Description                        |
| --------------- | ------ | ---------------------------------------- | ---------------------------------- |
| `agent_name`    | string | `patientAct`                             | Generator identifier               |
| `prompt_path`   | string | `data/prompts/generator/patientAct.yaml` | Path to prompt file                |
| `resource_dir`  | string | `data/resources/PatientAct`              | Priors and disease outlines        |
| `random_seed`   | int    | `null`                                   | Seeds the demographic sampler      |
| `model_type`    | string | `"OPENAI"`                               | Model provider key                 |
| `model_name`    | string | `"gpt-4o"`                               | Model identifier                   |
| `temperature`   | float  | `0.7`                                    | Sampling temperature               |
| `max_tokens`    | int    | `8192`                                   | Max response tokens                |
| `max_retries`   | int    | `3`                                      | API retry attempts                 |

## Seed Record Format

Seeds live in `data/seeds/patientAct.json` as a JSON list. Each record is validated against
`PatientActSeed` before generation — one character is produced per record:

```json
[
  {
    "disease_key": "anxiety_disorder",
    "topic": "health anxiety",
    "situation": "The patient is preoccupied with the conviction that a serious physical illness is being missed despite repeated medical reassurance and negative test results. The fear has narrowed into a persistent belief that cancer may be present and spreading undetected ..."
  }
]
```

| Field         | Type   | Description                                                              |
| ------------- | ------ | ------------------------------------------------------------------------ |
| `disease_key` | string | Selects the disease outline and prior overrides                          |
| `topic`       | string | Bookkeeping label; not used during generation                            |
| `situation`   | string | Referral-perspective description of what brought the patient to treatment |

## Output Format

One `PatientActCharacter` per record, written index-aligned to `data/characters/patientAct.json`:

```json
{
  "profile": {
    "demographics": { "...": "..." },
    "problem_formulation": { "...": "..." },
    "psychological_formulation": { "...": "..." }
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
  "situation": "The patient is preoccupied with the conviction that ...",
  "disease_key": "anxiety_disorder"
}
```

See the [PatientAct client](../clients/patientact.md#character-data-format) for the fully expanded profile.

## Required Data Files

`resource_dir` must contain three files:

| File                    | Contents                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| `attribute_priors.json` | `global` distributions for the six sampled attributes, plus `age_ranges`                  |
| `disease_priors.json`   | Per-disease overrides keyed by `disease_key`, as `{attribute: {labels: {...}}}`           |
| `disease_outlines.json` | Per-disease clinical outlines: key characteristics, typical presentation by severity, important notes, contraindications, differential considerations, special populations, red flags |

Outlines currently cover `adhd`, `anxiety_disorder`, `bipolar_disorder`, `depression`, `insomnia`, `ocd`, `ptsd`, and `schizophrenia`. A situation whose `disease_key` is missing from the outlines still generates — the model is told to infer the clinical context from the situation instead.

Note that `attribute_priors.json` deliberately omits the secure attachment style: `SampledDemographic` admits only the three insecure styles, so the remaining weights are renormalized at sampling time.
