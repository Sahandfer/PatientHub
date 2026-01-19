---
sidebar_position: 4
---

# Eeyore

> Eeyore: Realistic Depression Simulation via Expert-in-the-Loop Supervised and Preference Optimization

**Venue**: ACL 2025 (Findings)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.findings-acl.707/)

## Overview

Eeyore creates realistic simulations of individuals experiencing depression. The method was developed with expert validation to ensure clinical authenticity while being suitable for training and research purposes.

## Key Features

- **Expert Validation**: Developed with mental health professional input
- **Realistic Symptoms**: Models DSM-5 depression criteria
- **Varied Presentations**: Different severity levels and symptom profiles
- **Screening-Ready**: Designed for depression screening research

## Depression Symptoms Modeled

Based on DSM-5 Major Depressive Disorder criteria:

| Symptom             | Description                                       |
| ------------------- | ------------------------------------------------- |
| Depressed Mood      | Persistent sadness, emptiness, hopelessness       |
| Anhedonia           | Loss of interest in previously enjoyed activities |
| Sleep Disturbance   | Insomnia or hypersomnia                           |
| Fatigue             | Low energy, tiredness                             |
| Worthlessness       | Feelings of guilt, low self-esteem                |
| Concentration       | Difficulty thinking, making decisions             |
| Psychomotor Changes | Agitation or retardation                          |
| Appetite Changes    | Weight loss or gain                               |
| Suicidal Ideation   | Thoughts of death (handled carefully)             |

## Usage

### CLI

```bash
uv run python -m examples.simulate client=eeyore therapist=user
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'eeyore',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/Eeyore.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Clinician'})

response = client.generate_response("How have you been sleeping lately?")
print(response.content)
```

## Configuration

| Option      | Description            | Default                       |
| ----------- | ---------------------- | ----------------------------- |
| `data_path` | Path to character file | `data/characters/Eeyore.json` |
| `data_idx`  | Character index        | `0`                           |

## Character Data Format

```json
{
  "demographics": {
    "name": "Sam",
    "age": 34,
    "gender": "female",
    "occupation": "accountant"
  },
  "depression_profile": {
    "severity": "moderate",
    "duration": "6 months",
    "primary_symptoms": [
      "depressed_mood",
      "anhedonia",
      "fatigue",
      "sleep_disturbance"
    ],
    "triggers": ["Work stress", "Relationship difficulties"]
  },
  "presentation_style": {
    "verbal": "slow, quiet speech",
    "affect": "flat, sad",
    "engagement": "low but cooperative"
  },
  "background": "Recent job loss, living alone, limited social support"
}
```

## Example Conversation

**Clinician**: "Hi Sam, thank you for coming in. How have you been feeling lately?"

**Patient (Eeyore)**: "_sighs_ I don't know... just tired, I guess. Everything feels like such an effort. Even getting out of bed this morning took everything I had."

**Clinician**: "It sounds like you're experiencing a lot of fatigue. How long has this been going on?"

**Patient**: "Months now. I used to love going to yoga, seeing friends... now I can't remember the last time I did either. What's the point, really?"

**Clinician**: "You mentioned you used to enjoy yoga and seeing friends. What changed?"

**Patient**: "I lost my job back in March. I keep telling myself I'll start applying for new ones, but every time I sit down to work on my resume, I just... can't. I stare at the screen and think, 'Why would anyone hire me anyway?'"

## Severity Levels

### Mild Depression

- Some symptoms present
- Functional impairment limited
- Generally responsive to conversation

### Moderate Depression

- Multiple symptoms
- Noticeable functional impact
- Slower, more effortful engagement

### Severe Depression

- Most criteria met
- Significant impairment
- May mention hopelessness (safely handled)

## Safety Considerations

:::warning Important
Eeyore is designed for training and research only. If simulating suicidal ideation:

- Content is carefully worded
- No specific methods mentioned
- Focus on hopelessness rather than plans
- Designed to train appropriate clinical responses
  :::

## Research Applications

### Depression Screening Research

```python
# Test different screening approaches
screening_questions = [
    "Over the past two weeks, how often have you felt down, depressed, or hopeless?",
    "Over the past two weeks, how often have you had little interest or pleasure in doing things?",
]

responses = []
for q in screening_questions:
    r = client.generate_response(q)
    responses.append(r.content)
```

### Therapist Training

```bash
# Practice with varying severity
uv run python -m examples.simulate client=eeyore client.data_idx=0  # Mild
uv run python -m examples.simulate client=eeyore client.data_idx=1  # Moderate
uv run python -m examples.simulate client=eeyore client.data_idx=2  # Severe
```

## Evaluation

Evaluate clinical appropriateness:

```python
eval_config = OmegaConf.create({
    'eval_type': 'rating',
    'target': 'client',
    'dimensions': ['consistency', 'emotion'],
    'granularity': 'session',
    # ...
})
```

## Best Practices

1. **Warm, Empathetic Approach**: Respond to the simulated distress appropriately
2. **Open-Ended Questions**: Allow expression of symptoms
3. **Validate Feelings**: Acknowledge the difficulty of their experience
4. **Assess Function**: Ask about daily activities, sleep, appetite

## Limitations

- Simulates depression presentation, not underlying neurobiology
- Fixed symptom profile within a session
- Cultural presentation variations not fully modeled
- Should not replace clinical training with real patients

## Related Methods

- [TalkDep](/docs/methods/overview) - Also focused on depression, more screening-oriented
- [PatientPsi](/docs/methods/patientpsi) - Includes depressive symptoms in CBT context
