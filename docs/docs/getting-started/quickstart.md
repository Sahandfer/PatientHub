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
| `adaptiveVP`   | Nurse communication training                     |
| `simPatient`   | Cognitive model updates                          |
| `talkDep`      | Depression screening                             |
| `saps`         | State-aware medical patient                      |
| `clientCast`   | Psychotherapy assessment                         |
| `psyche`       | Psychiatric assessment                           |
| `roleplayDoh`  | Principle-based simulation                       |

## Available Therapists

| Therapist | Description                  |
| --------- | ---------------------------- |
| `user`    | Human input (default)        |
| `CBT`     | AI CBT therapist             |
| `eliza`   | Classic Eliza chatbot        |
| `bad`     | Poor therapist (for testing) |
| `cami`    | AI Motivational Interviewing therapist |
| `psyche`  | A therapist conducting a clinical interview |

## Python API

For more control, use the Python API directly:

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

# Configure the client
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

# Load the client
client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Dr. Smith'})

# Generate responses
response = client.generate_response("Hello, how are you feeling today?")
print(response)

response = client.generate_response("Can you tell me more about that?")
print(response)
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

:::tip TIPS
Session data is only saved when the event reaches its “end” action (i.e., it writes to `event.output_dir`).

All ways to trigger saving:
- The therapist’s output is exactly `END` / `end` / `exit` ⇒ session_ended=True ⇒ end and save
- The conversation reaches `event.max_turns` (num_turns >= max_turns) ⇒ end and save
:::

## Creating New Agents

You can run the following command to create the necessary files for a new agent:

```bash
uv run python -m examples.create generator.gen_agent_type=[client|therapist] generator.gen_agent_name=<agent_name>
```

For example

```bash
uv run python -m examples.create generator.gen_agent_type=client generator.gen_agent_name=test
```

## What's Next?

- [Learn about different components](/docs/components/overview)
- [Evaluate conversations](/docs/guide/evaluation)
- [Configuration options](/docs/getting-started/configuration)
