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
- **Progressive External Disclosure**: More external situations become visible when rapport is strong enough.
- **Progressive Internal Disclosure**: Internal cognitive elements are revealed one category at a time when therapist questions facilitate deeper exploration.
- **Difficulty Presets**: `easy`, `hard`, and `custom` control openness, metacognition, and initial visibility.
- **Mediator-Gated Updates**: Two mediator prompts judge rapport/openness and question facilitation during the session.

## How It Works

MindVoyager keeps a masked client profile in the system prompt. During the dialogue, the cognitive mediator decides whether the therapist has earned more disclosure.

1. **Rapport check**: every `rapport_check_interval` turns, the mediator rates rapport / openness. If the rating reaches `rapport_threshold`, the next external situation becomes visible.
2. **Question facilitation check**: every metacognition-dependent interval, the mediator rates whether the therapist's question promotes deeper self-exploration. If the rating reaches `question_threshold`, the next internal cognitive diagram category becomes visible.
3. **Prompt update**: after any reveal, the system prompt is rebuilt so the next client response reflects newly visible information while everything else remains masked.

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

Only the first `initial_visible_external_count` experiences are visible at initialization. Hidden experiences are rendered as:

```text
EXPERIENCE
Situation: unknown
Reactions: unknown
```

When the rapport mediator judges that the client has become sufficiently open, `reveal_next_external()` increases the number of visible external experiences by one. The upper bound is the number of external experiences in the character data.

### Internal Cognitive Diagram

Internal cognitive elements are hidden at initialization. Hidden values are rendered as `unknown` in the system prompt.

The implementation reveals internal elements in this order:

| Reveal order | Internal key |
| ------------ | ------------ |
| 1 | `relevant_history` |
| 2 | `core_beliefs` |
| 3 | `intermediate_beliefs` |
| 4 | `coping_strategies` |

When the question facilitation mediator judges that the therapist asked a sufficiently deep question, `reveal_internal()` reveals the next hidden internal category.

## Mediator Checks

MindVoyager uses two mediator checks. They correspond to the paper's two update routes: rapport-based external disclosure and metacognition/question-based internal disclosure.

| Dimension | Frequency control | What is judged | Success threshold | If successful |
| --------- | ----------------- | -------------- | ----------------- | ------------- |
| external | `rapport_check_interval` | Whether rapport / openness is sufficient | `rapport_threshold` | Reveal the next external situation |
| internal | `low_metacognition_question_check_interval` or `high_metacognition_question_check_interval` | Whether the therapist's question deeply facilitates inner exploration | `question_threshold` | Reveal the next internal cognitive diagram category |

### External Route: Rapport and Openness

Every `rapport_check_interval` therapist turns, the client runs `openness_critic_prompt`. The mediator returns an `OpennessAssessment` rating from 1 to 5.

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

then the client reveals the next internal cognitive diagram category.

This route models whether the therapist's question helps the client move from surface content toward deeper self-reflection.

## Difficulty Presets

The public config intentionally stays small:

| Option | Default | Description |
| ------ | ------- | ----------- |
| `agent_name` | `mindVoyager` | Client identifier |
| `prompt_path` | `data/prompts/client/mindVoyager.yaml` | Prompt file |
| `data_path` | `data/characters/mindVoyager.json` | Character file |
| `data_idx` | `0` | Character index |
| `difficulty` | `custom` | Preset name: `easy`, `hard`, or `custom` |

Behavioral settings live in `MindVoyagerClient.DIFFICULTY_PRESETS`:

| Preset field | Meaning | Typical effect |
| ------------ | ------- | -------------- |
| `openness` | How willing the client is to disclose thoughts, feelings, and experiences | `high` clients can be more detailed earlier; `low` clients rely more on rapport development |
| `metacognition` | How easily the client can reflect on internal patterns when prompted | `high` clients can be checked for internal exploration more often |
| `initial_visible_external_count` | Number of external experiences visible at session start | Higher values make the case easier because the therapist starts with more context |
| `low_metacognition_question_check_interval` | Internal mediator check interval when `metacognition` is `low` | Larger values make internal disclosure slower |
| `high_metacognition_question_check_interval` | Internal mediator check interval when `metacognition` is `high` | Smaller values make internal disclosure faster |

Current defaults:

| Difficulty | `openness` | `metacognition` | `initial_visible_external_count` | Low-meta interval | High-meta interval |
| ---------- | ---------- | --------------- | -------------------------------- | ----------------- | ------------------ |
| `easy` | `high` | `high` | `3` | `2` | `1` |
| `hard` | `low` | `low` | `1` | `2` | `1` |
| `custom` | `low` | `high` | `2` | `2` | `1` |

To customize the client profile, override the `custom` preset:

```python
from patienthub.clients.mindVoyager import MindVoyagerClient

MindVoyagerClient.DIFFICULTY_PRESETS["custom"] = {
    "openness": "high",
    "metacognition": "low",
    "initial_visible_external_count": 1,
    "low_metacognition_question_check_interval": 3,
    "high_metacognition_question_check_interval": 1,
}
```

## Class-Level Parameters

These parameters are class attributes because they describe the mediator protocol rather than the basic config surface.

| Parameter | Default | Meaning | When to adjust |
| --------- | ------- | ------- | -------------- |
| `rapport_check_interval` | `4` | Number of therapist turns between rapport/openness checks | Lower it to test faster external disclosure; raise it to make external disclosure slower |
| `rapport_threshold` | `4` | Minimum openness rating required to reveal another external experience | Lower it for more permissive external disclosure; raise it for stricter rapport requirements |
| `question_threshold` | `4` | Minimum question facilitation rating required to reveal internal content | Lower it for more permissive internal disclosure; raise it for stricter exploration requirements |

Example:

```python
from patienthub.clients import get_client

client = get_client(agent_name="mindVoyager", lang="en")
client.rapport_check_interval = 2
client.rapport_threshold = 3
client.question_threshold = 4
```

## Paper Alignment

The paper describes two mediator-controlled update loops:

- Every `k` turns, check rapport. If successful, increase accessible external information.
- Every `l` turns, check question facilitation based on metacognition. If successful, uncover more of the internal cognitive diagram.

In this implementation:

- `k` is represented by `rapport_check_interval`.
- `l` is represented by `low_metacognition_question_check_interval` or `high_metacognition_question_check_interval`.
- The success thresholds are represented by `rapport_threshold` and `question_threshold`.
- The paper prompt demonstrates three previous-experience slots, while this implementation renders external experiences dynamically from the character data.

The paper-sourced settings are also summarized in `data/resources/MindVoyager/paper_settings.json`.

## Usage

### CLI

```bash
patienthub simulate client=mindVoyager client.difficulty=easy
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name="mindVoyager", lang="en")
response = client.generate_response("What feels hardest to talk about today?")

print(response.content)
```

## Character Data Format

```json
{
  "id": "mindvoyager_001",
  "name": "Alex",
  "style": ["reserved", "hesitant"],
  "internal_cognitive_diagram": {
    "relevant_history": "Family conflict and previous substance abuse.",
    "core_beliefs": ["I am trapped."],
    "intermediate_beliefs": ["If I disappoint my family, I will lose them."],
    "coping_strategies": "Avoidance and emotional withdrawal."
  },
  "external_experiences": [
    {
      "situation": "Alex's cousin invited him to attend his upcoming wedding.",
      "reaction": "Alex felt tense and avoided replying."
    }
  ]
}
```

## Tuning Guide

Use `difficulty="easy"` when you want the therapist to start with more external context and a client who can reflect quickly.

Use `difficulty="hard"` when you want the therapist to work with low initial disclosure and slower internal access.

Use `difficulty="custom"` when you want to manually define the client profile through `DIFFICULTY_PRESETS["custom"]`.

For most experiments, tune the preset fields first. Adjust `rapport_check_interval`, `rapport_threshold`, or `question_threshold` only when you intentionally want to change the mediator protocol itself.
