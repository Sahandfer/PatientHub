# Interviewer

The Interviewer NPC conducts structured clinical interviews with clients, useful for intake assessments, diagnostic interviews, and research data collection.

## Overview

| Property  | Value                 |
| --------- | --------------------- |
| **Key**   | `interviewer`         |
| **Type**  | LLM-based             |
| **Focus** | Structured Interviews |

## Description

The Interviewer NPC is designed to conduct systematic, structured interviews following predefined protocols. It can be configured for various interview types including clinical intake, diagnostic assessment, and research data collection. The interviewer maintains a professional, neutral stance while gathering comprehensive information.

## Key Features

- **Structured Protocols** - Follows predefined interview scripts
- **Adaptive Follow-ups** - Asks clarifying questions based on responses
- **Multiple Interview Types** - Supports intake, diagnostic, and custom formats
- **Data Collection** - Captures structured responses for analysis

## Configuration

### YAML Configuration

```yaml
npc:
  type: interviewer
  config:
    model: gpt-4o
    interview_type: intake
    questions:
      - "What brings you here today?"
      - "Can you tell me about your current symptoms?"
```

### Python Usage

```python
from patienthub.npcs import NPCRegistry

interviewer = NPCRegistry.create("interviewer", config={
    "model": "gpt-4o",
    "interview_type": "intake"
})

response = interviewer.respond(conversation_history)
```

## Parameters

| Parameter        | Type   | Default  | Description                                   |
| ---------------- | ------ | -------- | --------------------------------------------- |
| `model`          | string | `gpt-4o` | The LLM model to use                          |
| `interview_type` | string | `intake` | Type of interview: intake, diagnostic, custom |
| `questions`      | list   | -        | Custom questions for the interview            |
| `follow_up`      | bool   | `true`   | Enable adaptive follow-up questions           |

## Interview Types

### Intake Interview

Standard clinical intake assessment covering:

- Presenting problems
- Symptom history
- Personal background
- Treatment goals

```yaml
npc:
  type: interviewer
  config:
    interview_type: intake
```

### Diagnostic Interview

Structured diagnostic assessment aligned with clinical criteria:

```yaml
npc:
  type: interviewer
  config:
    interview_type: diagnostic
    focus: ["depression", "anxiety"]
```

### Custom Interview

Define your own interview protocol:

```yaml
npc:
  type: interviewer
  config:
    interview_type: custom
    questions:
      - "How would you describe your sleep patterns?"
      - "What coping strategies have you tried?"
      - "Who do you turn to for support?"
```

## Use Cases

- **Intake assessments** - Gather initial client information
- **Diagnostic interviews** - Structured diagnostic evaluations
- **Follow-up evaluations** - Track progress over time
- **Research data collection** - Standardized data gathering
- **Training simulations** - Practice interview skills

## Example

```python
from patienthub.npcs import NPCRegistry
from patienthub.clients import get_client
from omegaconf import OmegaConf

# Create interviewer
interviewer = NPCRegistry.create("interviewer", config={
    "model": "gpt-4o",
    "interview_type": "intake"
})

# Create client
client_config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_name': 'gpt-4o',
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})
client = get_client(configs=client_config, lang='en')

# Run interview
conversation = []
interviewer_question = interviewer.start_interview()
conversation.append({"role": "interviewer", "content": interviewer_question})

client_response = client.generate_response(interviewer_question)
conversation.append({"role": "client", "content": client_response})

# Continue interview...
```
