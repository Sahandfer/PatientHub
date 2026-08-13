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
  "name": "Abe",
  "persona": {
    "name": "Abe",
    "age": "42 years old",
    "gender": "Male",
    "occupation": "Recently unemployed (former manager).",
    "family_background": "Father left when Abe was 11; his overburdened mother was critical when he could not meet her unrealistic expectations.",
    "interpersonal_relationships": "Recently divorced; reluctant to lean on his adult son or ask anyone for help.",
    "physical_condition": "No significant medical problems; reports low energy and disrupted sleep under stress.",
    "lifestyle": "Unemployed with little daily structure; avoids tasks that feel like tests of competence.",
    "chief_complaint": "Feels incompetent and like a failure after losing his job and his marriage; avoids challenges and asking for help."
  },
  "background": "The current counseling topic is treatment goal setting ...",
  "main_ccd": {
    "name": "Abe",
    "relevant_history": "Abe's father left when he was 11; his critical mother had unrealistic expectations. He recently lost his job and went through a divorce.",
    "core_beliefs": ["I am incompetent.", "I am a failure."],
    "intermediate_beliefs": [
      "If I try hard things I'll fail, so it's safer to avoid challenges.",
      "If I ask for help, people will see how incompetent I am."
    ],
    "coping_strategies": ["Avoids asking for help.", "Avoids challenges and difficult tasks."]
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
