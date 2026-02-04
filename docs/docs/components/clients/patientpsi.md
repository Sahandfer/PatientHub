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
uv run python -m examples.simulate client=patientPsi therapist=CBT
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/PatientPsi.json',
    'patient_type': 'upset',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Dr. Smith'})

response = client.generate_response("How have you been feeling lately?")
print(response)
```

## Configuration

| Option         | Description            | Default                           |
| -------------- | ---------------------- | --------------------------------- |
| `data_path`    | Path to character file | `data/characters/PatientPsi.json` |
| `data_idx`     | Character index        | `0`                               |
| `patient_type` | Behavior pattern       | `"upset"`                         |

## Character Data Format

```json
{
    "name": "Alex",
    "id": "1-1",
    "type": [
        "plain",
        "verbose",
        "go off on tangents",
        "hostile",
        "guarded",
        "ingratiating"
    ],
    "history": "The patient has a history of substance abuse and has been through rehab to overcome it. He has had issues with his family, particularly with his mother, where he has felt rejected and emotionally neglected. He has struggled with obesity since childhood, which has affected his self-esteem and body image. He also has a history of being victimized and bullied due to his weight.",
    "helpless_belief_current": [
        "I am trapped.",
        "I am out of control."
    ],
    "unlovable_belief_current": [
        "I am unlovable.",
        "I am undesirable, unwanted."
    ],
    "worthless_belief_current": [],
    "intermediate_belief": "Helpless: I'm just not very good at handling stress and I have poor self-control, which is why I need to not put myself in stressful situations. \n Unlovable: If I show my true self, people will reject me the way my mother rejected me.",
    "intermediate_belief_depression": "Helpless: There's nothing I can do to change my situation. I cannot control myself. \nUnlovable: I don't deserve to be happy, so why even try to stay clean?",
    "coping_strategies": "The patient has adopted avoidance as a coping strategy by distancing himself from his family to reduce exposure to negativity and conflict. He has started scheduling pleasant activities and planning his day ahead of time in order to maintain a sense of control over his emotions and circumstances.",
    "situation": "Alex's cousin invited him to attend his upcoming wedding.",
    "auto_thought": "It will be stressful and negative; people will ask me questions I cannot answer or don't want to answer; my mum would be ashamed of me and critical of me as always; They don't want me there anyway, nobody likes me in this family.",
    "emotion": [
        "anxious, worried, fearful, scared, tense",
        "sad, down, lonely, unhappy"
    ],
    "behavior": "Ignored the invitation and did not respond to the RSVP request. Ignored phone calls from family."
}
```
