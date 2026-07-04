# Deprofile

> Decomposing Clinical Profiles for Mental Health Patient Simulation

## Overview

Deprofile role-plays a patient built from a **decomposed clinical profile**: a
clinical assessment (symptoms, risks, Big Five), assessment and counseling
dialogue records, and a social-media timeline (symptoms and life events). At
simulation time, clinical positive/negative symptoms are rendered as
natural-language descriptions (with the symptom timeline woven into the positive
symptoms), and the life-event timeline is injected as rendered memory cards.

The character file consumed by this client is produced by the
[**Deprofile generator**](../generators/deprofile.md), which assembles and
validates these sources into a single `DeprofileCharacter` record. See that page
for the data pipeline, resource files, and output format.

## Key Features

- **Decomposed profile**: Combines a clinical profile with matched
  assessment/counseling dialogues and a social-media timeline.
- **Timeline memory**: Life events are surfaced from processed memory cards
  (`timeline_memory.life_event.cards[*].card_text`), falling back to the raw
  timeline when cards are unavailable.
- **Localized rendering**: Symptom descriptions and relative-time phrasing are
  drawn from localized constants (`en` / `zh`).

## Usage

### CLI

```bash
patienthub simulate client=deprofile
```

Simulate a specific character in the file by index:

```bash
patienthub simulate client=deprofile client.data_idx=0
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name='deprofile', lang='en')
response = client.generate_response("How have you been feeling this week?")
print(response.content)
```

## Configuration

| Option                  | Type | Default                              | Description                                     |
| ----------------------- | ---- | ------------------------------------ | ----------------------------------------------- |
| `prompt_path`           | str  | `data/prompts/client/deprofile.yaml` | Path to the role-play prompt file               |
| `data_path`             | str  | `data/characters/deprofile.json`     | Path to the generated character file            |
| `data_idx`              | int  | `0`                                  | Index of the character in the file              |
| `max_dialogue_snippets` | int  | `10`                                 | Max assessment/counseling snippets injected     |
| `max_timeline_items`    | int  | `50`                                 | Max symptom/life-event timeline items injected  |

Common API-model options (`model_type`, `model_name`, `temperature`,
`max_tokens`, `max_retries`, `lang`) are inherited from the shared client
configuration — see the [overview](./overview.md#configuration-options).

## Character Data Format

`data/characters/deprofile.json` is a JSON array of `DeprofileCharacter`
records. Each record carries the clinical profile, both dialogue records, the
selected social user's symptom and life-event timelines, and the processed
`timeline_memory` (graph, episodes, and memory cards). The full schema and an
annotated example are documented in the
[Deprofile generator → Output Format](../generators/deprofile.md#output-format).

To produce or extend this file, use the generator:

```python
from omegaconf import OmegaConf
from patienthub.generators import get_generator

config = OmegaConf.create({
    "agent_name": "deprofile",
    "profile_id": "0069",
    "output_path": "data/characters/deprofile.json",
})
generator = get_generator(agent_name="deprofile", configs=config, lang="zh")
character = generator.generate_character()
```

## See Also

- [Deprofile generator](../generators/deprofile.md) — how the character file is built.
- [Client Agents API](./overview.md) — shared configuration and loading.
