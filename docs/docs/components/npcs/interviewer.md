# Interviewer

The Interviewer NPC conducts structured scripted interviews with clients by sequentially delivering questions from a JSON file.

## Overview

| Property  | Value                 |
| --------- | --------------------- |
| **Key**   | `interviewer`         |
| **Type**  | Rule-based            |
| **Focus** | Structured Interviews |

## How It Works

1. **Data Loading**: Loads a list of questions from a JSON file at `configs.data`.
2. **Sequential Delivery**: Each `generate_response()` call records the incoming message and returns the next question in the list.
3. **Completion**: Returns `"[No more questions]"` when the question list is exhausted.

## Usage

### Python

```python
from omegaconf import OmegaConf
from patienthub.npcs.interviewer import InterviewerNPC

config = OmegaConf.create({"data": "data/evaluations/surveys/default_survey.json"})
interviewer = InterviewerNPC(configs=config)

question = interviewer.generate_response("start")
print(question)
```

## Configuration

| Parameter | Type   | Default                                        | Description                        |
| --------- | ------ | ---------------------------------------------- | ---------------------------------- |
| `data`    | string | `data/evaluations/surveys/default_survey.json` | Path to the questions JSON file    |

## Data Format

The questions file is a JSON array of strings:

```json
[
  "How have you been feeling this week?",
  "Have you experienced any changes in sleep or appetite?",
  "How would you rate your mood on a scale of 1–10?"
]
```

## Use Cases

- **Pre-session intake**: Administer a standardized questionnaire before therapy begins
- **Post-session evaluation**: Collect structured feedback from client agents
- **Research data collection**: Gather consistent responses across simulated sessions
- **Training simulations**: Practice interview skills with simulated clients

## Example: Intake Before Therapy

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.npcs.interviewer import InterviewerNPC

interviewer = InterviewerNPC(
    configs=OmegaConf.create({"data": "data/evaluations/surveys/default_survey.json"})
)
client = get_client(agent_name="patientPsi", lang="en")

question = interviewer.generate_response("start")
while question != "[No more questions]":
    print("Interviewer:", question)
    answer = client.generate_response(question)
    print("Client:", answer.content if hasattr(answer, "content") else answer)
    question = interviewer.generate_response(answer.content)
```
