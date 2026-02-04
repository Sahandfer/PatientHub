# LLM Judge

The LLM Judge evaluator uses large language models to assess therapy sessions across multiple dimensions.

## Overview

| Property  | Value                        |
| --------- | ---------------------------- |
| **Key**   | `llm_judge`                  |
| **Type**  | LLM-based                    |
| **Focus** | Multi-dimensional Assessment |

## Description

The LLM Judge is an AI-powered evaluation agent that analyzes therapy conversations and provides scores, feedback, and suggestions across multiple therapeutic dimensions. It leverages the reasoning capabilities of large language models to assess nuanced aspects of therapeutic interactions.

## Evaluation Criteria

The LLM Judge can evaluate sessions based on:

- **Empathy** - How well the therapist demonstrates understanding and compassion
- **Adherence** - Whether therapeutic techniques are properly applied
- **Effectiveness** - The potential therapeutic value of the session
- **Safety** - Appropriate handling of crisis situations
- **Rapport** - Quality of therapeutic alliance

## Configuration

### YAML Configuration

```yaml
evaluator:
  key: llm_judge
  config:
    model: gpt-4o
    temperature: 0.3
    criteria:
      - empathy
      - adherence
      - effectiveness
```

### Python Usage

```python
from patienthub.evaluators import EvaluatorRegistry

evaluator = EvaluatorRegistry.create("llm_judge", config={
    "model": "gpt-4o",
    "temperature": 0.3,
    "criteria": ["empathy", "adherence", "effectiveness"]
})

results = evaluator.evaluate(conversation_history)
```

## Parameters

| Parameter     | Type   | Default  | Description                                            |
| ------------- | ------ | -------- | ------------------------------------------------------ |
| `model`       | string | `gpt-4o` | The LLM model to use for evaluation                    |
| `temperature` | float  | `0.3`    | Controls response randomness (lower = more consistent) |
| `criteria`    | list   | all      | Which criteria to evaluate                             |

## Output Format

```python
{
    "overall_score": 0.85,
    "criteria_scores": {
        "empathy": 0.9,
        "adherence": 0.8,
        "effectiveness": 0.85
    },
    "feedback": "The therapist demonstrated strong empathy...",
    "suggestions": ["Consider exploring...", "Could improve..."]
}
```

## Use Cases

- **Therapist Training** - Automated feedback for trainee therapists
- **Research** - Consistent evaluation across large datasets
- **Quality Assurance** - Monitoring AI therapist performance
- **Benchmarking** - Comparing different therapeutic approaches

## Example

```python
from patienthub.evaluators import EvaluatorRegistry

# Create evaluator
evaluator = EvaluatorRegistry.create("llm_judge", config={
    "model": "gpt-4o",
    "criteria": ["empathy", "adherence", "safety"]
})

# Load conversation
conversation = [
    {"role": "therapist", "content": "How are you feeling today?"},
    {"role": "client", "content": "Not great, I've been really anxious..."},
    # ... more turns
]

# Evaluate
results = evaluator.evaluate(conversation)

print(f"Overall Score: {results['overall_score']}")
print(f"Empathy: {results['criteria_scores']['empathy']}")
print(f"Feedback: {results['feedback']}")
```
