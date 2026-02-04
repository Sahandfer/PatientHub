---
sidebar_position: 1
slug: /
---

# PatientHub

> A unified hub to create, simulate, and evaluate methods for patient/client simulation.

## What is PatientHub?

PatientHub is a comprehensive framework that brings together **12+ patient simulation methods** from leading AI and HCI venues (ACL, EMNLP, CHI, CIKM) into a single, easy-to-use toolkit.

### Key Features

- 🧠 **Multiple Patient Agents** - PatientPsi, ConsistentMI, Eeyore, and more
- 🧑‍⚕️ **Therapist Agents** - CBT, MI, Eliza, or human-in-the-loop
- 📊 **Built-in Evaluation** - Consistency, therapeutic alliance, emotion
- 🌐 **Web Demo** - Interactive Chainlit interface

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
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Dr. Smith'})

response = client.generate_response("How are you feeling today?")
print(response)
```

## Supported Methods

| Method | Venue | Focus |
| ------------------------------------------ | ----------------- | ------------------------- |
| [SAPS](/docs/methods/saps) | ArXiv | Clinical Diagnosis |
| [ConsistentMI](/docs/methods/consistentmi) | ACL 2025 | Motivational Interviewing |
| [Eeyore](/docs/methods/eeyore) | ACL 2025 Findings | Depression |
| [AnnaAgent](/docs/methods/annaagent) | ACL 2025 Findings | Multi-session Counseling |
| [AdaptiveVP](/docs/methods/adaptivevp) | ACL 2025 Findings | Nurse Communication Training |
| [SimPatient](/docs/methods/simpatient) | CHI 2025 | Alcohol Misuse |
| [TalkDep](/docs/methods/talkdep) | CIKM 2025 | Depression Screening |
| [ClientCAST](/docs/methods/clientcast) | Arxiv | Psychotherapy |
| [PSYCHE](/docs/methods/psyche) | ArXiv | Psychiatric Assessment |
| [PatientPsi](/docs/methods/patientpsi) | EMNLP 2024 | CBT |
| [RoleplayDoh](/docs/methods/roleplaydoh) | EMNLP 2024 | Counseling |

## Getting Started

Ready to dive in? Check out the [Installation Guide](/docs/getting-started/installation).
