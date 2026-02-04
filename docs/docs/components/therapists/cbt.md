# CBT Therapist

The CBT (Cognitive Behavioral Therapy) therapist implements evidence-based CBT techniques for therapeutic interventions.

## Overview

| Property  | Value                        |
| --------- | ---------------------------- |
| **Key**   | `cbt`                        |
| **Type**  | LLM-based                    |
| **Focus** | Cognitive Behavioral Therapy |

## Description

The CBT Therapist is an AI-powered therapeutic agent that employs evidence-based Cognitive Behavioral Therapy techniques. It is designed to help clients identify and challenge negative thought patterns, develop coping strategies, and understand the connection between thoughts, feelings, and behaviors.

## Key Techniques

- **Cognitive restructuring** - Identifying and challenging negative thought patterns
- **Behavioral activation** - Encouraging engagement in positive activities
- **Problem-solving** - Helping clients develop coping strategies
- **Psychoeducation** - Explaining the connection between thoughts, feelings, and behaviors

## Configuration

### YAML Configuration

```yaml
therapist:
  key: cbt
  config:
    model: gpt-4o
    temperature: 0.7
```

### Python Usage

```python
from patienthub.therapists import TherapistRegistry

therapist = TherapistRegistry.create("cbt", config={
    "model": "gpt-4o",
    "temperature": 0.7
})
```

## Parameters

| Parameter     | Type   | Default  | Description                  |
| ------------- | ------ | -------- | ---------------------------- |
| `model`       | string | `gpt-4o` | The LLM model to use         |
| `temperature` | float  | `0.7`    | Controls response randomness |

## Use Cases

- CBT training simulations
- Research on therapeutic techniques
- Educational demonstrations of CBT principles
