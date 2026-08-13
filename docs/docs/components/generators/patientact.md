# PatientAct

> Generates trust-gated client profiles from a clinical situation: samples a demographic scaffold from disease-conditioned priors, builds a case formulation in stages, validates it against a disease outline, then derives the disclosure memory.

## Overview

The PatientAct generator turns one clinical *situation* into one complete [PatientAct client](../clients/patientact.md). It runs in two halves:

1. **Profile construction** — sample a demographic scaffold from priors, then generate the problem formulation, demographics, and psychological formulation in sequence, each conditioned on what came before. The finished profile is checked against the full disease outline and regenerated with revision guidance if it fails.
2. **Memory construction** — walk the finished profile, extract every disclosable element, and assign each a disclosure level, activation tags, and a discomfort flag.

Splitting profile from memory matters: the profile is what the client *is*, the memory is what the client *will say and when*.

## Key Features

- **Disease-Conditioned Priors**: Demographic attributes are sampled from global priors, overridden per disease where epidemiological data supports it.
- **Staged Formulation**: Problem formulation, demographics, and psychological formulation are separate LLM calls, so each sees the previous output.
- **Deterministic Conflict Checks**: Regex rules catch scaffold/situation contradictions (a child with an office job, a male patient with postpartum evidence) before the model is asked to reconcile them.
- **Two-Tier Outlines**: Generation sees only key characteristics and typical presentation; validation additionally sees contraindications, differentials, and red flags.
- **Revision Loops**: Demographics retry up to 5 times, the whole profile up to 3, each time carrying forward the specific issues found.
- **Seeded Sampling**: `random_seed` reproduces the demographic scaffold of a single record.

## How It Works

### 1. Sample the demographic scaffold

Six attributes — `age_group`, `biological_sex`, `ethnicity`, `occupation_type`, `core_belief_theme`, `attachment_style` — are drawn by weighted choice from `attribute_priors.json`. When `disease_priors.json` has an override for the situation's `disease_key`, that distribution replaces the global one for the affected attribute.

### 2. Generate the problem formulation

The situation, the disease outline, and the scaffold minus its psychological attributes are given to the model. Core belief theme and attachment style are deliberately withheld here so the presenting problem is not written backwards from the intended psychology.

The result covers presenting problem, precipitating, predisposing, perpetuating, and protective factors.

### 3. Complete the demographics

Before asking the model, `hard_conflict_issues()` scans the situation and problem formulation for contradictions with the sampled scaffold:

| Scaffold             | Conflicting evidence                                                     |
| -------------------- | ------------------------------------------------------------------------ |
| `age_group: Child`   | Adult occupations; alcohol or adult-life language (married, coworker, …)  |
| `age_group: Elderly` | `occupation_type: Student`; child or adolescent language                 |
| `gender: male`       | Pregnancy, postpartum, or menopause language                             |

Any hits are passed in as revision guidance. The model returns a `DemographicCompletionResult`; if it does not pass, its own issues become the next round's guidance, up to 5 attempts. After that the last candidate is accepted and the remaining issues are logged as a warning.

### 4. Generate the psychological formulation

Now the core belief theme and attachment style are supplied, along with the demographics and problem formulation, to produce intermediate beliefs, automatic thoughts, triggers, coping patterns, emotional range, and interpersonal patterns.

### 5. Validate

The assembled profile is checked against the **full** disease outline — including contraindications, differential considerations, and red flags that generation never saw. On failure, `revision_guidance` is threaded back into all three generation steps and the profile is rebuilt, up to 3 attempts.

### 6. Build the memory

`extract_memory_items()` deterministically walks the profile and collects the disclosable elements: predisposing factors, intermediate beliefs, automatic thoughts, triggers, presenting-problem impacts, perpetuating factors, and interpersonal patterns. The `the therapist` interpersonal pattern is excluded — it drives the client's trust critic at simulation time, not disclosure.

The model then assigns each item a `disclosure_level`, 3–5 `activation_tags`, and a `generates_discomfort` flag.

## Resources

`resource_dir` (default `data/resources/PatientAct`) must contain:

| File                    | Contents                                                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| `attribute_priors.json` | `global` distributions for the six sampled attributes, plus `age_ranges`                        |
| `disease_priors.json`   | Per-disease overrides, keyed by `disease_key`, as `{attribute: {labels: {...}}}`                |
| `disease_outlines.json` | Per-disease clinical outlines: key characteristics, typical presentation by severity, important notes, contraindications, differential considerations, special populations, red flags |

Outlines currently cover `adhd`, `anxiety_disorder`, `bipolar_disorder`, `depression`, `insomnia`, `ocd`, `ptsd`, and `schizophrenia`. A situation whose `disease_key` is missing from the outlines still generates — the model is told to infer the clinical context from the situation instead.

## Input Format

Input records live in `data/seeds/patientAct.json` and are validated against `PatientActSeed`:

```json
{
  "disease_key": "anxiety_disorder",
  "topic": "health anxiety",
  "situation": "The patient is preoccupied with the conviction that a serious physical illness is being missed despite repeated medical reassurance and negative test results..."
}
```

`topic` is carried for bookkeeping; generation uses `situation` and `disease_key`.

## Configuration

| Option          | Default                                 | Description                                     |
| --------------- | --------------------------------------- | ----------------------------------------------- |
| `agent_name`    | `patientAct`                            | Generator identifier                            |
| `prompt_path`   | `data/prompts/generator/patientAct.yaml`| Prompt file                                     |
| `resource_dir`  | `data/resources/PatientAct`             | Priors and disease outlines                     |
| `random_seed`   | `null`                                  | Seeds the demographic sampler                   |

## Usage

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

`random_seed` defaults to `null` for a reason: one generator is built per input record, so a fixed integer seeds every record's RNG identically and the whole batch collapses onto a single demographic scaffold. Set it only when reproducing one record:

```bash
patienthub generate generator=patientAct input_path=data/seeds/patientAct.json \
    generator.random_seed=42 num_samples=1
```

## Output Format

One `PatientActCharacter` per input record, written index-aligned to `data/characters/patientAct.json`. See the [client documentation](../clients/patientact.md#character-data-format) for the full shape.
