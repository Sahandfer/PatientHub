---
sidebar_position: 2
---

# Quick Start

This guide will get you running your first patient simulation in under 5 minutes.

## Run a Simulation

The simplest way to start is with the CLI:

```bash
uv run python -m examples.simulate
```

This runs a therapy session with default settings (talkDep client, user therapist).

## Customize the Simulation

### Change the Patient Type

```bash
uv run python -m examples.simulate client=patientPsi
```

### Use an AI Therapist

```bash
uv run python -m examples.simulate client=patientPsi therapist=CBT
```

### Full Example

```bash
uv run python -m examples.simulate \
  client=consistentMI \
  therapist=CBT \
  event.max_turns=20
```

## Available Clients

| Client         | Description                                      |
| -------------- | ------------------------------------------------ |
| `patientPsi`   | CBT-focused patient simulation                   |
| `consistentMI` | Motivational Interviewing with stage transitions |
| `eeyore`       | Depression simulation                            |
| `annaAgent`    | Multi-session with memory                        |
| `simPatient`   | Cognitive model updates                          |
| `talkDep`      | Depression screening                             |
| `saps`         | State-aware medical patient                      |
| `clientCast`   | Psychotherapy assessment                         |

## Available Therapists

| Therapist | Description           |
| --------- | --------------------- |
| `user`    | Human input (default) |
| `CBT`     | AI CBT therapist      |
| `eliza`   | Classic Eliza chatbot |
| `basic`   | Simple AI therapist   |

## Python API

For more control, use the Python API directly:

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

# Configure the client
config = OmegaConf.create({
    'agent_type': 'patientPsi',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/PatientPsi.json',
    'data_idx': 0,
})

# Load the client
client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Dr. Smith'})

# Generate responses
response = client.generate_response("Hello, how are you feeling today?")
print(response.content)

response = client.generate_response("Can you tell me more about that?")
print(response.content)
```

## Interactive Web Demo

Launch the Chainlit web interface:

```bash
chainlit run app.py
```

Then open http://localhost:8000 in your browser.

## Output Files

Session data is saved to `data/sessions/` by default. You can customize this:

```bash
uv run python -m examples.simulate event.output_dir=outputs/my_session.json
```

## What's Next?

- [Learn about different patient agents](/docs/methods/overview)
- [Run batch experiments](/docs/guide/batch-processing)
- [Evaluate conversations](/docs/guide/evaluation)
- [Configuration options](/docs/getting-started/configuration)
