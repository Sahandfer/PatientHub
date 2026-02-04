---
sidebar_position: 3
---

# Evaluation

PatientHub provides multi-dimensional evaluation of simulated conversations.

## Evaluation Types

### Rating Evaluation

Score conversations using LLM-as-a-judge **scalar** evaluation (1–5 by default):

```bash
uv run python -m examples.evaluate \
  input_dir=data/sessions/default/badtherapist.json \
  output_dir=data/evaluations/session_scalar.json \
  evaluator.eval_type=scalar \
  evaluator.instruction_dir=data/prompts/evaluator/client/scalar.yaml
```

### Inspection Evaluation

Identify issues by extracting relevant passages with **extraction** evaluation:

```bash
uv run python -m examples.evaluate \
  input_dir=data/sessions/default/badtherapist.json \
  output_dir=data/evaluations/session_inspection.json \
  evaluator.eval_type=extraction \
  evaluator.instruction_dir=data/prompts/evaluator/client/inspect.yaml \
  evaluator.use_reasoning=true
```

## Evaluation Dimensions

### For Clients (Patients)

Client dimensions are defined in the instruction YAML (e.g. `data/prompts/evaluator/client/scalar.yaml`):

| Dimension           | Description                                                                       |
| ------------------- | --------------------------------------------------------------------------------- |
| `consistency`       | Consistency with profile and self-consistency across turns                        |
| `emotional_depth`   | Authenticity, complexity, and appropriateness of emotional expression              |
| `pedagogical_value` | Whether responses create learning opportunities and an appropriate challenge level |
| `engagement`        | Interaction quality: agreeableness, “self-curing” tendency, and realism           |

### For Therapists

Therapist dimensions are also instruction-driven (e.g. `data/prompts/evaluator/therapist/cbt.yaml`):

| Dimension                      | Description                                         |
| ----------------------------- | --------------------------------------------------- |
| `adherence_to_cbt_principles` | Adherence to CBT principles (rubric aspects in YAML) |

## Configuration

### LLM Judge Evaluator

```python
eval_config = {
    'agent_type': 'llm_judge',
    'eval_type': 'scalar',  # 'binary' | 'scalar' | 'extraction' | 'classification'
    'target': 'client',  # or 'therapist'
    'instruction_dir': 'data/prompts/evaluator/client/scalar.yaml',
    'granularity': 'session',  # 'turn', 'turn_by_turn', or 'session'
    'use_reasoning': False,
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_retries': 3,
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
session = load_json('data/sessions/default/badtherapist.json')

# Configure evaluator
eval_config = OmegaConf.create({
    'agent_type': 'llm_judge',
    'eval_type': 'scalar',
    'target': 'client',
    'instruction_dir': 'data/prompts/evaluator/client/scalar.yaml',
    'granularity': 'session',
    'use_reasoning': False,
    'model_type': 'OPENAI',
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

### Scalar Output

```json
{
  "consistency": {
    "profile_factual": {
      "score": 4
    },
    "conv_factual": {
      "score": 5
    },
    "behavioral": {
      "score": 4
    },
    "emotional": {
      "score": 4
    }
  }
}
```

### Extraction Output

```json
{
  "consistency": {
    "profile_factual": {
      "extracted_passages": [
        "Client: ..."
      ],
      "reasoning": "..."
    }
  }
}
```

## Custom Dimensions

Dimensions and aspects live in the instruction YAML (under `dimensions:`). To customize, edit or copy an instruction file and update the `instruction_dir` in your config.

Example (add a dimension entry to your YAML):

```yaml
dimensions:
  - name: therapeutic_alliance
    description: Quality of therapeutic relationship
    range: [1, 5]
    aspects:
      - name: rapport
        description: Level of connection
      - name: trust
        description: Client's apparent trust
```

## Batch Evaluation

Evaluate multiple sessions:

```python
from pathlib import Path
from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator
from omegaconf import OmegaConf

eval_config = OmegaConf.create({
    'agent_type': 'llm_judge',
    'eval_type': 'scalar',
    'target': 'client',
    'instruction_dir': 'data/prompts/evaluator/client/scalar.yaml',
    'granularity': 'session',
    'use_reasoning': False,
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_retries': 3,
})

evaluator = get_evaluator(configs=eval_config, lang='en')

input_dir = Path('data/sessions')
output_dir = Path('outputs/evaluations')
output_dir.mkdir(parents=True, exist_ok=True)

results = {}
for session_file in input_dir.rglob('*.json'):
    session = load_json(str(session_file))
    eval_result = evaluator.evaluate(session)
    results[str(session_file)] = eval_result

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
    if 'consistency' not in result:
        continue
    aspect_scores = [
        v['score'] for v in result['consistency'].values()
        if isinstance(v, dict) and 'score' in v
    ]
    if aspect_scores:
        scores.append(statistics.mean(aspect_scores))

print(f"Mean: {statistics.mean(scores):.2f}")
print(f"Std: {statistics.stdev(scores):.2f}")
print(f"Min: {min(scores)}, Max: {max(scores)}")
```

## Integration with Simulations

Run a simulation to generate a session JSON, then evaluate it:

```bash
uv run python -m examples.simulate \
  client=patientPsi \
  therapist=CBT
```

```bash
uv run python -m examples.evaluate \
  input_dir=data/sessions/default/session_1.json \
  output_dir=data/evaluations/session_1_scalar.json \
  evaluator.eval_type=scalar \
  evaluator.instruction_dir=data/prompts/evaluator/client/scalar.yaml
```

## Next Steps

- [API Reference: Evaluators](/docs/api/evaluators) - Detailed evaluator API
- [Contributing: New Evaluators](/docs/contributing/new-evaluators) - Add custom evaluators
