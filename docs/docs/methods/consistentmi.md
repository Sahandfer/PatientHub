---
sidebar_position: 3
---

# ConsistentMI

> Consistent Client Simulation for Motivational Interviewing-based Counseling

**Venue**: ACL 2025 (Main Conference)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.acl-long.1021/)

## Overview

ConsistentMI simulates clients in motivational interviewing (MI) sessions with consistent behavior based on the Transtheoretical Model (Stages of Change). The client's responses adapt based on their current stage and the therapist's MI techniques.

## Key Features

- **Stage of Change Model**: Precontemplation → Contemplation → Preparation → Action → Maintenance
- **Consistent Behavior**: Actions match the current stage
- **Stage Transitions**: Natural progression based on therapist's approach
- **MI-Specific Responses**: Reacts appropriately to OARS techniques

## Stages of Change

| Stage            | Description            | Typical Behaviors                     |
| ---------------- | ---------------------- | ------------------------------------- |
| Precontemplation | Not considering change | Denial, resistance, minimization      |
| Contemplation    | Aware but ambivalent   | Weighing pros/cons, uncertainty       |
| Preparation      | Planning to change     | Seeking information, small steps      |
| Action           | Actively changing      | Implementing changes, seeking support |
| Maintenance      | Sustaining change      | Preventing relapse, building habits   |

## Usage

### CLI

```bash
uv run python -m examples.simulate client=consistentMI therapist=MI
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'consistentMI',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/ConsistentMI.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Counselor'})

# Client starts in precontemplation
response = client.generate_response(
    "I noticed you mentioned you've been drinking more lately. How do you feel about that?"
)
print(response.content)
```

## Configuration

| Option      | Description            | Default                             |
| ----------- | ---------------------- | ----------------------------------- |
| `data_path` | Path to character file | `data/characters/ConsistentMI.json` |
| `data_idx`  | Character index        | `0`                                 |

## Character Data Format

```json
{
  "name": "Jordan",
  "age": 32,
  "presenting_issue": "alcohol use",
  "background": "Recently divorced, using alcohol to cope with stress",
  "initial_stage": "precontemplation",
  "change_topic": "reducing alcohol consumption",
  "motivations": [
    "Health concerns",
    "Relationship with children",
    "Job performance"
  ],
  "barriers": ["Social pressure", "Stress relief habit", "Fear of boredom"],
  "stage_behaviors": {
    "precontemplation": [
      "Minimize the problem",
      "Blame external factors",
      "Show defensiveness"
    ],
    "contemplation": [
      "Express ambivalence",
      "Ask questions about change",
      "Acknowledge some concerns"
    ]
  }
}
```

## How It Works

### State Machine

```
┌─────────────────┐     Good MI      ┌──────────────┐
│ Precontemplation│ ──────────────► │ Contemplation │
└─────────────────┘                  └──────────────┘
        ▲                                   │
        │ Poor MI                    Good MI│
        │                                   ▼
┌───────┴─────────┐                 ┌──────────────┐
│   Resistance    │ ◄────────────── │  Preparation │
└─────────────────┘    Poor MI      └──────────────┘
```

### Action Selection

The client selects actions based on:

1. **Current Stage**: Determines available action types
2. **Therapist Technique**: Responds to MI-appropriate approaches
3. **Topic Engagement**: Reacts to how well therapist addresses concerns

### Example Actions by Stage

**Precontemplation:**

- "I don't really see the big deal. Lots of people drink after work."
- "My ex is the one with the problem, not me."

**Contemplation:**

- "I mean, I guess I have been drinking more than I used to..."
- "Part of me knows I should cut back, but it's hard."

**Preparation:**

- "I've been thinking about trying to have alcohol-free weekdays."
- "What do you think about those apps that track drinking?"

## Example Conversation

**Therapist**: "Thanks for coming in today. What brings you here?"

**Client (Precontemplation)**: "My boss made me come. Apparently someone complained about smelling alcohol on my breath at work. I think they're overreacting—I just had a couple drinks at lunch."

**Therapist**: "It sounds frustrating to feel like others are making a big deal out of something. What's your take on your drinking?"

**Client**: "I mean, I drink, sure. But I'm not an alcoholic or anything. I can stop whenever I want. I just don't want to right now. Work's been stressful."

**Therapist** (using reflection): "Work stress has been a factor, and you feel in control of your drinking."

**Client** (slight shift): "Well... I guess sometimes I drink more than I plan to. But who doesn't, right?"

## MI Techniques That Promote Change

| Technique      | Example                                  | Effect               |
| -------------- | ---------------------------------------- | -------------------- |
| Open Questions | "What concerns you about your drinking?" | Elicits change talk  |
| Affirmations   | "It takes courage to talk about this."   | Builds self-efficacy |
| Reflections    | "You're worried about your health."      | Shows understanding  |
| Summaries      | "So you've mentioned..."                 | Organizes thoughts   |

## Evaluating MI Skills

Use with the `rating` evaluator:

```bash
uv run python -m examples.evaluate \
  evaluator=rating \
  evaluator.target=therapist \
  evaluator.dimensions=[active_listening]
```

## Best Practices

1. **Use MI Therapist**: Pair with `therapist=MI` for best results
2. **Watch for Change Talk**: Client will express change talk when therapist uses good MI
3. **Avoid Confrontation**: Confrontational approaches trigger resistance
4. **Track Stage**: Note when client shows signs of stage transition

## Limitations

- Stage transitions may not perfectly match clinical expectations
- Cultural factors not explicitly modeled
- Binary resistance model (engaged vs. resistant)

## Related Methods

- [SimPatient](/docs/methods/overview) - Also models cognitive states in MI context
- [PatientPsi](/docs/methods/patientpsi) - CBT-focused alternative
