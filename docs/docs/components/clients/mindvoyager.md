---
sidebar_position: 7
---

# MindVoyager

> A cognitive-diagram client agent that reveals external situations and internal beliefs through mediator-gated therapeutic dialogue.

**Venue**: ACL 2025 (Findings)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.findings-acl.1332/)

## Overview

MindVoyager simulates a psychotherapy client whose full cognitive conceptualization is not visible at the beginning of the session. The client is initialized with a masked cognitive diagram and a limited number of visible external experiences. As the therapist builds rapport and asks deeper questions, a cognitive mediator periodically evaluates the dialogue and unlocks more information.

This makes MindVoyager different from a static role-play client: the therapist cannot access the whole case profile immediately. The client gradually becomes more open when the conversation demonstrates enough rapport or enough exploratory depth.

## Key Features

- **Masked Cognitive Diagram**: Internal elements start hidden and are rendered as `unknown` in the system prompt.
- **Progressive External Disclosure**: One more external situation becomes visible when rapport is strong enough.
- **All-at-Once Internal Disclosure**: The entire internal cognitive diagram is revealed in a single step when therapist questions facilitate deep enough exploration.
- **Difficulty Presets**: `easy`, `normal`, `hard`, and `custom` control openness, metacognition, and initial visibility.
- **Mediator-Gated Updates**: Two mediator prompts judge rapport/openness and question facilitation during the session.

## How It Works

MindVoyager keeps a masked client profile in the system prompt. During the dialogue, the cognitive mediator decides whether the therapist has earned more disclosure.

1. **Rapport check**: every `rapport_interval` turns, the mediator rates rapport / openness. If the rating reaches `rapport_threshold`, one more external situation becomes visible.
2. **Question facilitation check**: every metacognition-dependent interval, the mediator rates whether the therapist's question promotes deeper self-exploration. If the rating reaches `question_threshold`, the entire internal cognitive diagram becomes visible.
3. **Prompt update**: after any reveal, the system prompt is rebuilt so the next client response reflects newly visible information while everything else remains masked. If nothing was revealed on a turn, the prompt is left unchanged.

## Masking and Disclosure

MindVoyager separates the client case into two information layers.

### External Experiences

External experiences are observable life situations and reactions. The agent renders this section dynamically from the character data:

```text
PREVIOUS EXPERIENCE 1
PREVIOUS EXPERIENCE 2
PREVIOUS EXPERIENCE 3
...
```

Only the first `visible_external_count` experiences are visible at initialization. Hidden experiences are rendered as:

```text
PREVIOUS EXPERIENCE 2
Situation: unknown
Reactions: unknown
```

When the rapport mediator judges that the client has become sufficiently open, `reveal_next_external()` increases the number of visible external experiences by one. The upper bound is the number of external experiences in the character data.

### Internal Cognitive Diagram

Internal cognitive elements are hidden at initialization and rendered as `unknown` in the system prompt. The diagram has four categories:

| Internal key           |
| ---------------------- |
| `relevant_history`     |
| `core_beliefs`         |
| `intermediate_beliefs` |
| `coping_strategies`    |

When the question facilitation mediator judges that the therapist asked a sufficiently deep question, `reveal_internal()` unmasks the **entire** internal cognitive diagram at once (all four categories). This follows the paper, where a passing quality check unmasks the full internal diagram rather than one element at a time.

## Mediator Checks

MindVoyager uses two mediator checks. They correspond to the paper's two update routes: rapport-based external disclosure and metacognition/question-based internal disclosure. Both critics run through the same model the client uses and return a structured `1-5` rating.

| Dimension | Frequency control                                                                           | What is judged                                                        | Success threshold    | If successful                                |
| --------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------------------- | -------------------------------------------- |
| external  | `rapport_interval`                                                                          | Whether rapport / openness is sufficient                              | `rapport_threshold`  | Reveal one more external situation           |
| internal  | `low_metacognition_question_check_interval` or `high_metacognition_question_check_interval` | Whether the therapist's question deeply facilitates inner exploration | `question_threshold` | Reveal the entire internal cognitive diagram |

### External Route: Rapport and Openness

Every `rapport_interval` therapist turns, the client runs `openness_critic_prompt`. The mediator returns an `OpennessAssessment` rating from 1 to 5.

If:

```python
rating >= rapport_threshold
```

then the client reveals one more external experience.

This route models the idea that low-openness clients disclose more external life context only after the therapist establishes enough rapport.

### Internal Route: Question Facilitation

Every `l` therapist turns, the client runs `question_facilitation_prompt`. The value of `l` depends on the current metacognition setting:

- high metacognition: `high_metacognition_question_check_interval`
- low metacognition: `low_metacognition_question_check_interval`

The mediator returns a `QuestionFacilitationAssessment` rating from 1 to 5.

If:

```python
rating >= question_threshold
```

then the client reveals the entire internal cognitive diagram.

This route models whether the therapist's question helps the client move from surface content toward deeper self-reflection.

## Difficulty Presets

The public config intentionally stays small:

| Option         | Default                                | Description                                        |
| -------------- | -------------------------------------- | -------------------------------------------------- |
| `agent_name`   | `mindVoyager`                          | Client identifier                                  |
| `prompt_path`  | `data/prompts/client/mindVoyager.yaml` | Prompt file                                        |
| `data_path`    | `data/characters/mindVoyager.json`     | Character file                                     |
| `data_idx`     | `0`                                    | Character index                                    |
| `preset_level` | `easy`                                 | Preset name: `easy`, `normal`, `hard`, or `custom` |

Behavioral settings live in `patienthub.schemas.mindVoyager.DIFFICULTY_PRESETS`:

| Preset field                                 | Meaning                                                                   | Typical effect                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `openness`                                   | How willing the client is to disclose thoughts, feelings, and experiences | `high` clients can be more detailed earlier; `low` clients rely more on rapport development |
| `metacognition`                              | How easily the client can reflect on internal patterns when prompted      | `high` clients can be checked for internal exploration more often                           |
| `visible_external_count`                     | Number of external experiences visible at session start                   | Higher values make the case easier because the therapist starts with more context           |
| `low_metacognition_question_check_interval`  | Internal mediator check interval when `metacognition` is `low`            | Larger values make internal disclosure slower                                               |
| `high_metacognition_question_check_interval` | Internal mediator check interval when `metacognition` is `high`           | Smaller values make internal disclosure faster                                              |

Current defaults:

| Difficulty | `openness` | `metacognition` | `visible_external_count` | Low-meta interval | High-meta interval |
| ---------- | ---------- | --------------- | ------------------------ | ----------------- | ------------------ |
| `easy`     | `high`     | `high`          | `3`                      | `2`               | `1`                |
| `normal`   | `high`     | `low`           | `2`                      | `2`               | `1`                |
| `hard`     | `low`      | `low`           | `1`                      | `2`               | `1`                |
| `custom`   | `low`      | `high`          | `2`                      | `2`               | `1`                |

To customize the client profile, override the `custom` preset:

```python
from patienthub.schemas.mindVoyager import DIFFICULTY_PRESETS

DIFFICULTY_PRESETS["custom"] = {
    "openness": "high",
    "metacognition": "low",
    "visible_external_count": 1,
    "low_metacognition_question_check_interval": 3,
    "high_metacognition_question_check_interval": 1,
}
```

## Mediator Protocol Constants

The mediator protocol values follow the paper and live in `patienthub.schemas.mindVoyager.CONSTANTS`, shared across all instances:

| Constant             | Default | Meaning                                                                            |
| -------------------- | ------- | ---------------------------------------------------------------------------------- |
| `rapport_interval`   | `4`     | Number of therapist turns between rapport/openness checks                          |
| `rapport_threshold`  | `4`     | Minimum openness rating (1-5) required to reveal another external experience       |
| `question_threshold` | `4`     | Minimum question-facilitation rating (1-5) required to reveal the internal diagram |

The question-facilitation _interval_ is not a constant — it comes from the active difficulty preset (`low_`/`high_metacognition_question_check_interval`), since it depends on the client's metacognition level.

To change the protocol, edit the module-level dictionary:

```python
from patienthub.schemas.mindVoyager import CONSTANTS

CONSTANTS["rapport_interval"] = 2
CONSTANTS["rapport_threshold"] = 3
```

## Paper Alignment

The paper describes two mediator-controlled update loops:

- Every `k` turns, check rapport. If successful, increase accessible external information.
- Every `l` turns, check question facilitation based on metacognition. If successful, uncover the internal cognitive diagram.

In this implementation:

- `k` is `CONSTANTS["rapport_interval"]`.
- `l` is `low_metacognition_question_check_interval` or `high_metacognition_question_check_interval` from the active preset.
- The success thresholds are `CONSTANTS["rapport_threshold"]` and `CONSTANTS["question_threshold"]`.
- A passing rapport check reveals one more external situation; a passing question-facilitation check reveals the full internal diagram at once.
- The paper prompt demonstrates three previous-experience slots, while this implementation renders external experiences dynamically from the character data.

## Usage

### CLI

```bash
patienthub simulate client=mindVoyager client.preset_level=easy
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name="mindVoyager", lang="en")
response = client.generate_response("What feels hardest to talk about today?")

print(response.content)
```

## Character Data Format

MindVoyager profiles are derived from PatientPsi-style CBT profiles because both are organized around cognitive diagrams. In the MindVoyager paper, the cognitive elements come from Cognitive Conceptualization Diagrams annotated in the Patient-Ψ-CM dataset. A PatientPsi patient (whose situations are stored as separate rows sharing the same beliefs) is adapted into MindVoyager format by grouping those rows into one client and splitting the case into two layers:

- `internal_cognitive_diagram`: relevant history, core beliefs, intermediate beliefs, and coping strategies (merged across the patient's rows).
- `external_experiences`: situations and reactions that can be progressively disclosed (one per source row).

```json
{
  "source": "patientPsi-1",
  "name": "Abe",
  "internal_cognitive_diagram": {
    "relevant_history": "Father leaves family when Abe is 11 years old. Mom is overburdened and criticizes when he can't meet her unrealistic expectations. He then loses his job and undergoes divorce.",
    "core_beliefs": ["I am incompetent.", "I am a failure."],
    "intermediate_beliefs": [
      "It's important to be responsible, competent, reliable and helpful.",
      "During depression: If I try to do hard things I'll fail."
    ],
    "coping_strategies": "Avoids asking for help and avoids challenges."
  },
  "external_experiences": [
    {
      "situation": "Thinking about bills.",
      "reaction": "Automatic thoughts: What if I run out of money? Emotions: anxious, worried, fearful, scared, tense. Behavior: Continues to sit on couch; ruminates about his failures."
    }
  ]
}
```

## Tuning Guide

Use `preset_level="easy"` when you want the therapist to start with more external context and a client who can reflect quickly.

Use `preset_level="hard"` when you want the therapist to work with low initial disclosure and slower internal access.

Use `preset_level="normal"` for a middle ground (open but less self-aware), or `preset_level="custom"` to define the client behavior yourself through `DIFFICULTY_PRESETS["custom"]`.

For most experiments, tune the preset fields first. Adjust the `CONSTANTS` values only when you intentionally want to change the mediator protocol itself.
