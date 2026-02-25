---
sidebar_position: 1
slug: /
---

# PatientHub

> A unified hub to create, simulate, and evaluate methods for patient/client simulation.

## What is PatientHub?

PatientHub is a comprehensive framework that brings together **11 patient simulation methods** from leading AI and HCI venues (ACL, EMNLP, CHI, CIKM) into a single, easy-to-use toolkit.

### Key Features

- 🧠 **Multiple Patient Agents** - PatientPsi, ConsistentMI, Eeyore, and more
- 🧑‍⚕️ **Therapist Agents** - CBT, MI, or human-in-the-loop
- 📊 **Automatic Evaluation** - Customizable LLM-as-a-judge

## Quick Example

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
    'patient_type': 'upset',
    'prompt_path': 'data/prompts/client/patientPsi.yaml',
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')

response = client.generate_response("How are you feeling today?")
print(response)
```

## Getting Started

Ready to dive in? Check out the [Installation Guide](/docs/getting-started/installation).
