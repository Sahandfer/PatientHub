---
sidebar_position: 12
---

# CARS

> When Clients Stop Following: A Cognitive Conceptualization Diagram-driven Framework for Strategic Counseling

**Venue**: arXiv preprint (2026)  
**Paper**: [arXiv](https://arxiv.org/abs/2606.04389)

## Overview

CARS (**C**ognitive **A**lignment & **R**esistance **S**imulator) simulates a CBT client whose **resistance emerges dynamically** from Cognitive Conceptualization Diagrams (CCDs) rather than being scripted. It models when and why a client disengages from counselor guidance, providing a challenging test-bed for a therapist's exploration ability.

## Key Features

- **Dual CCD structure**: A stable main CCD (relevant history, core/intermediate beliefs, coping strategies) plus a session-specific CCD (automatic thought, intermediate belief, resistance triggers).
- **Dynamic resistance reasoning**: Each turn checks whether the topic triggers a resistance schema and whether the counselor's strategy confirms or conflicts with the client's beliefs.
- **Emotion state (0-100)**: Updated by a signed delta each turn; extremely low emotion ends the session.
- **Style-modulated cooperation**: A preferred counselor style and individual traits shape whether the client cooperates or resists.

## How It Works

1. **Profile Loading**: Loads a client profile — persona, background, main + session CCDs, preferences, and characteristics.
2. **Structured Reasoning**: Each turn the model reasons over topic → schema trigger → strategy-consistency check → updated cognition, emotion, and interaction goal.
3. **Response Generation**: Produces a structured turn (step-by-step reasoning, signed emotion change, intention, nonverbal behavior, and the final utterance).
4. **State Update**: Clamps emotion to 0-100, carries the interaction goal into the next turn, and ends the session if emotion falls to/below the termination threshold.

## Usage

### CLI

```bash
patienthub simulate client=cars
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name="cars", lang="en")

response = client.generate_response("Let's set some treatment goals for today. How does that sound?")
print(response)
```

## Configuration

| Option                  | Description                             | Default                         |
| ----------------------- | --------------------------------------- | ------------------------------- |
| `prompt_path`           | Path to prompt file                     | `data/prompts/client/cars.yaml` |
| `data_path`             | Path to character file                  | `data/characters/cars.json`     |
| `data_idx`              | Character index                         | `0`                             |
| `initial_emotion_state` | Starting emotion (0-100)                | `50`                            |
| `termination_threshold` | Emotion at/below which the session ends | `10`                            |

## Character Data Format

```json
{
  "name": "Alex",
  "persona": {
    "name": "Alex",
    "age": "23 years old",
    "gender": "Male",
    "occupation": "Unemployed",
    "family_background": "Raised largely by a critical, demanding parent whose approval was rare and tied to achievement.",
    "interpersonal_relationships": "Few close relationships; withdraws when he anticipates judgment.",
    "physical_condition": "No significant medical problems; reports low energy and disrupted sleep under stress.",
    "lifestyle": "Unemployed and living alone with little daily structure; avoids tasks that feel like tests.",
    "chief_complaint": "Sensitive to structured goal-setting because formal goals can feel like evaluation and proof of incompetence."
  },
  "background": "The current counseling topic is treatment goal setting ...",
  "main_ccd": {
    "name": "Alex",
    "relevant_history": "Grew up with a highly critical parent; past attempts at change were abandoned partway.",
    "core_beliefs": ["I am trapped.", "I am a failure."],
    "intermediate_beliefs": [
      "If I set a goal and fail, it proves I am incompetent."
    ],
    "coping_strategies": ["Avoidance of goal-setting and commitment."]
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
    "resistance_triggers": ["Authoritative or commanding goal-setting"]
  },
  "preferences": { "positive": ["..."], "negative": ["..."] },
  "client_characteristics": {
    "possible_responses_under_different_emotions": ["..."],
    "other_client_characteristics": ["..."]
  }
}
```

CARS characters can be authored by hand or produced by the [CARS generator](../generators/cars.md).

## Emotion-Utterance Corpus

The paper's response step (§3.1.2) selects sentence patterns from a _"pre-defined emotion-utterance corpus."_ The authors do not publish that corpus, so PatientHub does **not** ship one and it is not wired into the CARS prompt — the client generates its utterance directly from its reasoning and current emotion. This is a deliberate omission to avoid fabricating content the paper does not provide.
