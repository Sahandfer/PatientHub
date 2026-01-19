---
sidebar_position: 3
---

# Evaluation

PatientHub provides multi-dimensional evaluation of simulated conversations.

## Evaluation Types

### Rating Evaluation

Score conversations on multiple dimensions:

```bash
uv run python -m examples.evaluate \
  --input_dir data/sessions/default/session.json \
  --output data/evaluations/session_rating.json \
  evaluator=rating
```

### Inspection Evaluation

Identify specific issues in conversations:

```bash
uv run python -m examples.evaluate \
  --input_dir data/sessions/default/session.json \
  --output data/evaluations/session_inspection.json \
  evaluator=inspect
```

## Evaluation Dimensions

### For Clients (Patients)

| Dimension     | Description                                   |
| ------------- | --------------------------------------------- |
| `consistency` | Character consistency throughout conversation |
| `emotion`     | Emotional authenticity and appropriateness    |
| `resistance`  | Natural resistance patterns                   |

### For Therapists

| Dimension          | Description               |
| ------------------ | ------------------------- |
| `cbt`              | CBT technique application |
| `active_listening` | Active listening skills   |
| `pedagogical`      | Teaching effectiveness    |

## Configuration

### Rating Evaluator

```python
eval_config = {
    'eval_type': 'rating',
    'target': 'client',  # or 'therapist'
    'dimensions': ['consistency', 'emotion'],
    'granularity': 'session',  # 'turn', 'turn_by_turn', or 'session'
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
}
```

### Granularity Options

- **session**: Evaluate the entire conversation at once
- **turn**: Evaluate only the last turn
- **turn_by_turn**: Evaluate each turn individually

## Python API

```python
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator
from patienthub.utils import load_json

# Load session data
session = load_json('data/sessions/default/session.json')

# Configure evaluator
eval_config = OmegaConf.create({
    'eval_type': 'rating',
    'target': 'client',
    'dimensions': ['consistency'],
    'granularity': 'session',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_retries': 3,
})

# Run evaluation
evaluator = get_evaluator(configs=eval_config, lang='en')
results = evaluator.evaluate(session)

print(results)
```

## Output Format

### Rating Output

```json
{
  "consistency": {
    "character_adherence": {
      "score": 8,
      "comments": "The patient maintained consistent personality traits..."
    },
    "factual_consistency": {
      "score": 9,
      "comments": "No contradictions in stated facts..."
    },
    "overall_score": 8
  }
}
```

### Inspection Output

```json
{
  "consistency": {
    "character_adherence": {
      "issues": ["Turn 5: Patient suddenly became very talkative..."],
      "comments": ["This contradicts earlier established personality..."]
    }
  }
}
```

## Custom Dimensions

Create custom evaluation dimensions in `patienthub/evaluators/dimensions/`:

```python
# patienthub/evaluators/dimensions/my_dimension.py
from .base import Dimension, Aspect

MY_DIMENSION = Dimension(
    name="therapeutic_alliance",
    description="Quality of therapeutic relationship",
    aspects=[
        Aspect(
            name="rapport",
            description="Level of connection between therapist and client",
        ),
        Aspect(
            name="trust",
            description="Client's apparent trust in the therapist",
        ),
    ],
    target="therapist",
)
```

Register in `patienthub/evaluators/dimensions/__init__.py`:

```python
from .my_dimension import MY_DIMENSION

DIMENSION_REGISTRY = {
    # ...existing...
    "therapeutic_alliance": MY_DIMENSION,
}
```

## Batch Evaluation

Evaluate multiple sessions:

```python
import os
from pathlib import Path
from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator
from omegaconf import OmegaConf

eval_config = OmegaConf.create({
    'eval_type': 'rating',
    'target': 'client',
    'dimensions': ['consistency'],
    'granularity': 'session',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_retries': 3,
})

evaluator = get_evaluator(configs=eval_config, lang='en')

input_dir = Path('outputs/batch/2026-01-19')
output_dir = Path('outputs/evaluations/2026-01-19')
output_dir.mkdir(parents=True, exist_ok=True)

results = {}
for session_file in input_dir.glob('*.json'):
    if session_file.name == 'batch_summary.json':
        continue

    session = load_json(str(session_file))
    eval_result = evaluator.evaluate(session)
    results[session_file.name] = eval_result

save_json(results, str(output_dir / 'all_evaluations.json'))
```

## Aggregating Scores

```python
import json
import statistics

with open('outputs/evaluations/all_evaluations.json') as f:
    evaluations = json.load(f)

scores = []
for session_name, result in evaluations.items():
    if 'consistency' in result:
        scores.append(result['consistency']['overall_score'])

print(f"Mean: {statistics.mean(scores):.2f}")
print(f"Std: {statistics.stdev(scores):.2f}")
print(f"Min: {min(scores)}, Max: {max(scores)}")
```

## Integration with Simulations

Evaluate during simulation:

```bash
uv run python -m examples.simulate \
  client=patientPsi \
  therapist=CBT \
  evaluator=rating \
  evaluator.dimensions=[consistency,emotion]
```

## Next Steps

- [API Reference: Evaluators](/docs/api/evaluators) - Detailed evaluator API
- [Contributing: New Evaluators](/docs/contributing/new-evaluators) - Add custom evaluators
