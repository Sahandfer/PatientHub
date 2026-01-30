---
sidebar_position: 11
---

# RoleplayDoh

>  Enabling Domain-Experts to Create LLM-simulated Patients via Eliciting and Adhering to Principles

**Venue**: EMNLP 2024 (Main)  
**Paper**: [ACL Anthology](https://aclanthology.org/2024.emnlp-main.591/)

## Overview

RoleplayDoh aims to construct high-quality "AI simulated patients" in the medical field. (specifically mental health) The work introduces 123 distinct principles. These principles are created through two primary methods: Automatic Conversion via interactive feedback (Kudos, Critique, and Rewrite) between domain experts and the simulated patient, and Manual Writing by the experts themselves. 

In subsequent generations, the AI simulated patient utilizes these **expert-generated principles** to refine its responses through a pipeline.

## Key Features
- **Principle-as-Questions**: Decompose complex principles into simple "Yes/No" questions. 
> For example, split "Keep responses short and avoid using the word anxious" into "Is the response short?" and "Does the response avoid using the word anxious?".
- **Applicability Check**: Determine whether a principle is applicable in the current dialogue context
- **Self-Refine**: After the LLM generates a preliminary response, it uses the questions above for self-evaluation. If the answer to any question is "No," it regenerates the response based on the evaluation results.

## Usage

### CLI TODO:

```bash
uv run python -m examples.simulate client=saps therapist=user
```

### Python 

```python 
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create(
    {
        "agent_type": "roleplayDoh",
        "model_type": "LAB",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 1024,
        "max_retries": 3,
        "data_path": "data/characters/PatientPsi.json",
        "principles": "data/resources/roleplayDohPrinciple.json",
        "data_idx": 0,
    }
)

client = get_client(configs=config, lang="en")
client.set_therapist({"name": "Dr. Smith"})

response = client.generate_response("What brings you in today?")
print(response)
```

## Configuration

| Option      | Description            | Default                             |
| ----------- | ---------------------- | ----------------------------------- |
| `principles` | The Principles from experts | `data/resources/roleplayDohPrinciple.json`   |
| `data_path` | Path to character file | `data/characters/PatientPsi.json`   |
| `data_idx`  | Character index        | `0`                                 |
> the current way in our implement is selecting principles randomly

## Principle Format


```json
"3": [
        "When discussing personal struggles, be concise and direct in expressing the main issue without delving into unnecessary details.",
        "When describing personal struggles, provide an honest and detailed account of the experiences and emotions involved, without exaggeration or understatement.",
        "When discussing personal struggles, provide more detailed and specific examples to help the listener understand the depth of your experiences. For example, instead of saying 'I'm constantly worried about my appearance and what I eat', you could say 'I find myself scrutinizing my body in the mirror multiple times a day, and I often feel guilty after eating anything that I perceive as unhealthy.'"
    ],
```

## Resources

`data/resources/roleplayDohPrinciple.json`: The Principles generated from expert feedback reflect the common issues that arise when AI roleplays as a patient.
