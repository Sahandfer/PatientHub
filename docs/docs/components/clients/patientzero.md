# PatientZero

> Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data

**Paper**: [Arxiv](https://arxiv.org/pdf/2509.11078)

## Overview

PatientZero role-plays a patient from a clinically grounded **synthetic record**
generated without real patient data. Each record follows the paper's static
definition `P = {B, S, E}` — background patient profile, symptom trajectory, and
examination results — sampled from disease knowledge and attribute priors across
controlled demographic and severity distributions.

The character file consumed by this client is produced by the
[**PatientZero generator**](../generators/patientzero.md), which standardizes
disease knowledge, samples attributes, and validates each case before saving.
See that page for the generation pipeline, supported diseases, and how to add a
new disease.

## Key Features

- **Disease-grounded**: Records are built from standardized disease outlines and
  disease-specific attribute priors.
- **Distribution control**: Demographics, severity, and lifestyle are sampled
  from global and disease-specific priors.
- **Rich clinical detail**: Each case carries symptoms, a mental status exam,
  scale assessments, and a risk assessment.

## Usage

### CLI

```bash
patienthub simulate client=patientZero
```

Simulate a specific record in the file by index:

```bash
patienthub simulate client=patientZero client.data_idx=0
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name='patientZero', lang='en')
response = client.generate_response("What brings you in today?")
print(response.content)
```

## Configuration

| Option        | Type | Default                               | Description                            |
| ------------- | ---- | ------------------------------------- | -------------------------------------- |
| `prompt_path` | str  | `data/prompts/client/patientZero.yaml` | Path to the role-play prompt file      |
| `data_path`   | str  | `data/characters/patientZero.json`     | Path to the generated character file   |
| `data_idx`    | int  | `0`                                    | Index of the record in the file        |

Common API-model options (`model_type`, `model_name`, `temperature`,
`max_tokens`, `max_retries`, `lang`) are inherited from the shared client
configuration — see the [overview](./overview.md#configuration-options).

## Character Data Format

`data/characters/patientZero.json` is a JSON array of synthetic patient records.
The role-play client uses `patient_profile`, `symptom_trajectory`, and
`examination_results`; generator metadata may also be present. The full schema
and an annotated example are documented in the
[PatientZero generator → Output Format](../generators/patientzero.md#output-format).

To produce or extend this file, use the generator:

```python
from omegaconf import OmegaConf
from patienthub.generators import get_generator

config = OmegaConf.create({
    "agent_name": "patientZero",
    "disease_key": "depression",
    "output_path": "data/characters/patientZero.json",
})
generator = get_generator(agent_name="patientZero", configs=config, lang="en")
generator.generate_character()
```

## See Also

- [PatientZero generator](../generators/patientzero.md) — how the character file is built.
- [Client Agents API](./overview.md) — shared configuration and loading.
