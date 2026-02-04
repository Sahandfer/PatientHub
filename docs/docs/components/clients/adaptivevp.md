---
sidebar_position: 5
---

# AdaptiveVP

> A Framework for LLM-Based Virtual Patients that Adapts to Trainees' Dialogue to Facilitate Nurse Communication Training

**Venue**: ACL 2025 (Findings)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.findings-acl.118/)

## Overview

AdaptiveVP creates virtual patients for nurse communication training that adapt their responses based on the trainee's communication quality. It evaluates nurse responses on multiple dimensions (tone, empathy, de-escalation techniques) and adjusts patient behavior accordingly, making it ideal for training healthcare professionals in handling difficult patient interactions.

## Key Features

- **Adaptive Responses**: Patient behavior adapts based on nurse's communication quality
- **Multi-Dimensional Assessment**: Evaluates tone (calm, clear), empathy level (0-6 scale), and de-escalation techniques
- **Patient Personality Types**: Overdependent, Overly Authoritative, Aggressive and Uncooperative
- **Stage Directions**: Dynamic response guidance based on conversation context
- **Rich Output**: Generates inner monologue, verbal response, and non-verbal cues

## How It Works

1. **Nurse Input Analysis**: Evaluates the nurse's communication on tone, empathy, and de-escalation
2. **Stage Direction Selection**: Chooses appropriate response direction based on analysis
3. **Response Generation**: Creates response with inner thoughts, verbal content, and non-verbal cues
4. **Safety Monitoring**: Reviews the generated response to ensure it remains within professional boundaries, aligns with the patient profile, and adheres to the adaptation direction.

## Patient Types

| Type          | Description                                  | Typical Behaviors                        |
| ------------- | -------------------------------------------- | ---------------------------------------- |
| Dependent     | Requires constant attention and reassurance  | Frequent calls, anxiety, seeking comfort |
| Authoritarian | Emphasizes status, demands special treatment | Complaints, threats, dismissive of staff |
| Aggressive    | Responds with hostility when demands not met | Loud voice, threatening, confrontational |
|Uncooperative	| Passive-aggressive or refuses to engage in care	| Ignoring staff, feigning sleep, delaying treatment |

The original study validated these profiles within a South Korean nursing context, but the framework is adaptable to other cultural settings.

## Evaluation Dimensions

AdaptiveVP evaluates nurse communication on:

### Tone Assessment

- **Calm**: Did the nurse suppress contempt, frustration, anger, or anxiety?
- **Clear**: Did the nurse use clear sentences to reduce confusion?

### Empathy Level (0-6 scale)

Assesses the depth of emotional understanding and validation

### De-escalation Techniques

- **Autonomy**: Offering choices, seeking permission
- **Limit Setting**: Establishing clear behavioral boundaries
- **Problem Solving**: Clarifying issues, redirecting focus

### Prohibited Behaviors

- Premature empathy ("I understand" without justification)
- Invalidating beliefs
- Dismissive commands ("Calm down")

## Usage

### CLI

```bash
uv run python -m examples.simulate client=adaptiveVP therapist=user
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'adaptiveVP',
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/AdaptiveVP.json',
    'dir_path': 'data/resources/AdaptiveVP_stage_direction.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Nurse'})

response = client.generate_response("I understand you're feeling anxious. Would you like to talk about what's on your mind?")
print(f"Response: {response.content}")
print(f"Inner thoughts: {response.inner_monologue}")
print(f"Non-verbal: {response.non_verbal}")
```

## Configuration

| Option      | Description              | Default                                          |
| ----------- | ------------------------ | ------------------------------------------------ |
| `data_path` | Path to character file   | `data/characters/AdaptiveVP.json`                |
| `dir_path`  | Path to stage directions | `data/resources/AdaptiveVP_stage_direction.json` |
| `data_idx`  | Character index          | `0`                                              |

## Character Data Format

```json
{
  "id": 0,
  "type": 1,
  "type-text": "Dependent",
  "name": "Im Kyung",
  "situation": "A patient with a dependent tendency continuously calls the nurse...",
  "Chief complaint": "'Nurse, I'm so sorry... My chest is pounding...'",
  "gender": "Female",
  "age": 55,
  "religion": "Non-religious",
  "height": "162cm",
  "weight": "58kg",
  "Main symptom": "Anxiety and insomnia due to breast cancer",
  "History of present illness": "Diagnosed with breast lump 2 weeks ago...",
  "social history": "Freelance designer, divorced, no children",
  "past medical history": "Depression (5 years)",
  "past surgical history & date": "Appendectomy (20 years ago)",
  "family medical history": "Sister - breast cancer",
  "allergies": "Latex",
  "medication": "Escitalopram 10mg daily",
  "primary diagnosis": "Right breast cancer stage 2",
  "communication_summary": "The patient has a dependent personality...",
  "first_statement": "Nurse, could I have a quick word with you?"
}
```

## Response Format

AdaptiveVP generates structured responses with three components:

```python
class Response(BaseModel):
    inner_monologue: str  # Patient's internal thoughts
    content: str          # Verbal response to the nurse
    non_verbal: str       # Non-verbal communication/actions
```

