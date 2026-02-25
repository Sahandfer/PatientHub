# ClientCast Generator

The ClientCast Generator creates diverse client characters with a focus on variety and representation across different demographics, disorders, and presentation styles.

## Overview

| Property   | Value                      |
| ---------- | -------------------------- |
| **Key**    | `clientCast`               |
| **Type**   | LLM-based                  |
| **Output** | ClientCast character files |

## Description

The ClientCast Generator is designed to produce a wide variety of client profiles, ensuring diversity in demographics, presenting problems, and communication styles. It's particularly useful for creating large datasets of synthetic clients for training and research.

## Key Features

- **Diversity Focus** - Ensures representation across demographics
- **Batch Generation** - Efficiently creates multiple profiles
- **Customizable Constraints** - Control the diversity parameters
- **Assessment-Ready** - Characters include evaluation-friendly metadata

## Configuration

### YAML Configuration

```yaml
generator:
  type: clientCast
  config:
    model: gpt-4o
    temperature: 0.9
    diversity: high
```

### Python Usage

```python
from patienthub.generators import GeneratorRegistry

generator = GeneratorRegistry.create("clientCast", config={
    "model": "gpt-4o",
    "diversity": "high"
})

character = generator.generate({
    "disorder_category": "mood",
    "complexity": "moderate"
})
```

## Parameters

| Parameter     | Type   | Default                                  | Description                        |
| ------------- | ------ | ---------------------------------------- | ---------------------------------- |
| `prompt_path` | string | `data/prompts/generator/clientCast.yaml` | Path to prompt file                |
| `model`       | string | `gpt-4o`                                 | The LLM model to use               |
| `temperature` | float  | `0.9`                                    | Higher values increase diversity   |
| `diversity`   | string | `high`                                   | Diversity level: low, medium, high |

## Batch Generation

ClientCast excels at generating diverse batches:

```python
from patienthub.generators import GeneratorRegistry

generator = GeneratorRegistry.create("clientCast")

# Generate 10 diverse profiles
profiles = generator.batch_generate(
    count=10,
    diversity_constraints={
        "disorders": ["depression", "anxiety", "ptsd"],
        "age_range": [18, 65],
        "balance_gender": True,
        "include_minorities": True
    }
)
```

## Output Format

```json
{
  "id": "cc_001",
  "demographics": {
    "age": 34,
    "gender": "female",
    "ethnicity": "Hispanic",
    "occupation": "Teacher"
  },
  "clinical": {
    "presenting_problem": "Generalized anxiety affecting work...",
    "disorder": "GAD",
    "severity": "moderate"
  },
  "personality": {
    "communication_style": "verbose",
    "openness": "moderate"
  }
}
```

## Use Cases

- Building large, diverse training datasets
- Creating representative client populations for research
- Generating test cases for therapist agent evaluation
- Educational demonstrations of client diversity
