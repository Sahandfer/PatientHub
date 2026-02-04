# Psyche Generator

The Psyche Generator creates psychologically rich client profiles with detailed cognitive models, emotional patterns, and behavioral tendencies for psychiatric assessment simulations.

## Overview

| Property   | Value                  |
| ---------- | ---------------------- |
| **Key**    | `psyche`               |
| **Type**   | LLM-based              |
| **Output** | Psyche character files |

## Description

The Psyche Generator produces highly detailed psychological profiles that include cognitive distortions, emotional regulation patterns, defense mechanisms, and other clinically relevant characteristics. These profiles are designed for use in psychiatric assessment training and research.

## Key Features

- **Deep Psychological Modeling** - Detailed cognitive and emotional profiles
- **Clinical Accuracy** - Aligned with diagnostic criteria
- **Multi-faceted Evaluation** - Supports comprehensive assessment
- **Symptom Clusters** - Realistic symptom presentations

## Configuration

### YAML Configuration

```yaml
generator:
  type: psyche
  config:
    model: gpt-4o
    temperature: 0.7
    clinical_depth: high
```

### Python Usage

```python
from patienthub.generators import GeneratorRegistry

generator = GeneratorRegistry.create("psyche", config={
    "model": "gpt-4o",
    "clinical_depth": "high"
})

character = generator.generate({
    "disorder": "major_depression",
    "include_comorbidities": True
})
```

## Parameters

| Parameter        | Type   | Default  | Description                                 |
| ---------------- | ------ | -------- | ------------------------------------------- |
| `model`          | string | `gpt-4o` | The LLM model to use                        |
| `temperature`    | float  | `0.7`    | Controls generation randomness              |
| `clinical_depth` | string | `high`   | Level of clinical detail: low, medium, high |

## Output Format

```json
{
  "id": "psy_001",
  "demographics": {
    "age": 42,
    "gender": "male"
  },
  "diagnosis": {
    "primary": "Major Depressive Disorder",
    "specifiers": ["recurrent", "moderate"],
    "comorbidities": ["Generalized Anxiety Disorder"]
  },
  "cognitive_profile": {
    "distortions": ["catastrophizing", "all-or-nothing"],
    "core_beliefs": ["I am worthless", "Nothing will improve"],
    "automatic_thoughts": [...]
  },
  "emotional_profile": {
    "predominant_affect": "dysphoric",
    "emotional_regulation": "poor",
    "defense_mechanisms": ["denial", "intellectualization"]
  },
  "behavioral_patterns": {
    "sleep": "insomnia",
    "appetite": "decreased",
    "social_withdrawal": true
  },
  "symptom_severity": {
    "PHQ9_equivalent": 18,
    "GAD7_equivalent": 12
  }
}
```

## Use Cases

- Psychiatric assessment training simulations
- Creating clinically accurate test cases
- Research on diagnostic processes
- Building comprehensive patient case libraries
- Training AI models for mental health applications
