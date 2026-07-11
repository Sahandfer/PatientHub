---
sidebar_position: 10
---

# PatientPsi

> PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals

**Venue**: EMNLP 2024 (Main Conference)  
**Paper**: [ACL Anthology](https://aclanthology.org/2024.emnlp-main.711/)

## Overview

PatientPsi creates realistic patient simulations based on **cognitive behavioral therapy (CBT)** principles. It models patients with specific cognitive distortions, core beliefs, and automatic thoughts.

## Key Features

- **Cognitive Model**: Implements CBT cognitive model (Relevant History, Core Beliefs, Intermediate Beliefs, Coping Strategies...)
- **Conversational Styles**: Defines 6 conversational styles (Plain, Upset, Verbose, Reserved, Tangent, Pleasing)
- **CBT-Grounded**: Uses CBT profiles as a ground truth to evaluate trainees/therapists' ability.

## How It Works

1. **Profile Loading**: Loads a patient persona with CBT-relevant background (history, beliefs, coping strategies, situation, emotions, automatic thoughts).
2. **CBT-Grounded Prompt**: Builds a system prompt that uses the CBT cognitive conceptualization to guide responses.
3. **Style Conditioning**: Applies a configurable conversational style (e.g., upset/verbose/reserved/tangent/pleasing) to shape tone and disclosure patterns.
4. **Contextual Dialogue**: Keeps multi-turn conversation history so later replies reflect prior turns and gradually reveal deeper concerns.

## Usage

### CLI

```bash
patienthub simulate client=patientPsi
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name="patientPsi", lang='en')

response = client.generate_response("How have you been feeling lately?")
print(response)
```

## Configuration

| Option         | Description            | Default                               |
| -------------- | ---------------------- | ------------------------------------- |
| `prompt_path`  | Path to prompt file    | `data/prompts/client/patientPsi.yaml` |
| `data_path`    | Path to character file | `data/characters/patientPsi.json`     |
| `data_idx`     | Character index        | `0`                                   |
| `patient_type` | Behavior pattern       | `"plain"`                             |

## Character Data Format

The shipped `data/characters/patientPsi.json` contains the single illustrative
example ("Abe") released by the PATIENT-Ψ authors, across three situations
(`id` `1-1`, `1-2`, `1-3`) that share the same beliefs. The full annotated
Patient-Ψ-CM dataset is not redistributed here.

:::note Accessing the full dataset

To get access to the Patient-Ψ-CM dataset, please fill out [this form](https://forms.gle/pQ3g6YVFrEWjBU2H7). See the authors' repository at [ruiyiw/patient-psi](https://github.com/ruiyiw/patient-psi) for more details.

:::

```json
{
  "name": "Abe",
  "id": "1-1",
  "type": ["plain", "verbose", "tangent", "upset", "reserved", "pleasing"],
  "history": "Father leaves family when Abe is 11 years old. He never sees him again. Mom is overburdened, criticizes when he can't meet her unrealistic expectations. Precipitants to current disorder: Abe struggles and then loses his job and undergoes divorce.",
  "helpless_belief": ["I am incompetent.", "I am a failure."],
  "unlovable_belief": [],
  "worthless_belief": [],
  "intermediate_belief": "It's important to be responsible, competent, reliable and helpful. It's important to work hard and be productive.\n[during depression]\n(1) If I avoid challenges, I'll be okay, but if I try to do hard things I'll fail. (2) If I avoid asking for help, my incompetence won't show but if I do ask for help, people will see how incompetent I am.",
  "coping_strategies": "Avoids asking for help and avoids challenges.",
  "situation": "Thinking about bills.",
  "auto_thought": "What if I run out of money?",
  "emotion": ["anxious, worried, fearful, scared, tense"],
  "behavior": "Continues to sit on couch; ruminates about his failures."
}
```

The three core-belief fields (`helpless_belief`, `unlovable_belief`,
`worthless_belief`) are lists and may be empty. Newer profiles embed
depression-phase beliefs inside `intermediate_belief` under a
`[during depression]` marker; the optional `intermediate_belief_depression`
field is supported for backward compatibility.
