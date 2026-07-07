---
sidebar_position: 3
---

# Evaluation

PatientHub provides multi-dimensional evaluation of simulated conversations and generated profiles using LLM-as-a-judge evaluators.

## Evaluators

PatientHub ships two evaluators, selected by `agent_name`:

- `conv_judge`: evaluates a therapy session (conversation).
- `profile_judge`: evaluates a generated client profile.

Each evaluator reads its scoring schema from a prompt YAML (`prompt_path`). The scoring paradigm for each dimension is defined inside that YAML, not on the config.

### Conversation Evaluation

Score a session with `conv_judge`:

```bash
patienthub evaluate \
  input_dir=data/sessions/default/badtherapist.json \
  output_dir=data/evaluations/session_conv.json \
  evaluator=conv_judge \
  evaluator.granularity=session
```

### Profile Evaluation

Evaluate a generated client profile with `profile_judge`:

```bash
patienthub evaluate \
  input_dir=data/sessions/default/badtherapist.json \
  output_dir=data/evaluations/profile.json \
  evaluator=profile_judge \
  evaluator.use_reasoning=true
```

### Resuming an Interrupted Run

The output is checkpointed after every session, so an interrupted run keeps its
progress. Pass `resume=true` to keep the already-evaluated sessions in the
existing output and (re-)evaluate only the missing or failed ones:

```bash
patienthub evaluate \
  input_dir=data/sessions/default \
  resume=true
```

## Evaluation Dimensions

Dimensions are defined in the prompt YAML referenced by `prompt_path`. Each dimension has a `name`, a `description`, and either a list of `aspects` or a scoring `paradigm`. For example, the bundled `data/prompts/evaluator/client_conv.yaml` defines client dimensions such as:

| Dimension           | Description                                                                        |
| ------------------- | ---------------------------------------------------------------------------------- |
| `consistency`       | Consistency with profile and self-consistency across turns                         |
| `emotional_depth`   | Authenticity, complexity, and appropriateness of emotional expression              |
| `pedagogical_value` | Whether responses create learning opportunities and an appropriate challenge level |
| `engagement`        | Interaction quality: agreeableness, “self-curing” tendency, and realism            |

To change or add dimensions, edit the prompt YAML (see [Custom Dimensions](#custom-dimensions)) rather than the config.

## Configuration

### Conv Judge Config

`ConvJudgeConfig` fields (subclass of `LLMJudgeConfig` → `APIModelConfig`):

```python
from patienthub.evaluators import ConvJudgeConfig  # or build a dict/OmegaConf

eval_config = {
    'agent_name': 'conv_judge',
    'prompt_path': 'data/prompts/evaluator/client_conv.yaml',
    'granularity': 'session',  # 'session' | 'turn' | 'turn_by_turn'
    'use_reasoning': False,
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 8192,
    'max_retries': 3,
}
```

`profile_judge` uses the same fields except that it has no `granularity` (its `prompt_path` defaults to `data/prompts/evaluator/client_profile.yaml`).

### Granularity Options

- **session**: Evaluate the entire conversation at once
- **turn**: Evaluate only the last turn
- **turn_by_turn**: Evaluate each turn individually

## Python API

`get_evaluator` takes `agent_name` as a required positional argument. Pass `configs` to override the defaults, or omit it to use the evaluator's default config.

```python
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator
from patienthub.utils import load_json

# Load session data
session = load_json('data/sessions/default/badtherapist.json')

# Configure evaluator
eval_config = OmegaConf.create({
    'agent_name': 'conv_judge',
    'prompt_path': 'data/prompts/evaluator/client_conv.yaml',
    'granularity': 'session',
    'use_reasoning': False,
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 8192,
    'max_retries': 3,
})

# Run evaluation
evaluator = get_evaluator(agent_name='conv_judge', configs=eval_config, lang='en')
results = evaluator.evaluate(session)

print(results)
```

To use the built-in defaults, call `get_evaluator(agent_name='conv_judge', lang='en')` without a `configs` argument.

## Output Format

The output shape follows the prompt's `dimensions`. A dimension with `aspects` nests one result per aspect; a dimension with a bare `paradigm` returns a single result.

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

Extraction dimensions return a `snippets` list. With `use_reasoning=true`, each judged item also gets a `reasoning` field:

```json
{
  "consistency": {
    "profile_factual": {
      "snippets": ["Client: ..."],
      "reasoning": "..."
    }
  }
}
```

## Custom Dimensions

Dimensions and aspects live in the prompt YAML (under `dimensions:`). To customize, edit or copy a prompt file and point `prompt_path` at it.

Example (add a dimension entry to your YAML):

A dimension either declares a `paradigm` directly, or lists `aspects` that inherit the dimension's `paradigm` and `range`:

```yaml
dimensions:
  - name: therapeutic_alliance
    description: Quality of therapeutic relationship
    paradigm: scalar
    range: [1, 5]
    aspects:
      - name: rapport
        description: Level of connection
      - name: trust
        description: Client's apparent trust
```

Supported paradigms are `binary`, `scalar`, `categorical`, and `extraction`.

## Batch Evaluation

Evaluate multiple sessions:

```python
from pathlib import Path
from patienthub.utils import load_json, save_json
from patienthub.evaluators import get_evaluator
from omegaconf import OmegaConf

eval_config = OmegaConf.create({
    'agent_name': 'conv_judge',
    'prompt_path': 'data/prompts/evaluator/client_conv.yaml',
    'granularity': 'session',
    'use_reasoning': False,
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 8192,
    'max_retries': 3,
})

evaluator = get_evaluator(agent_name='conv_judge', configs=eval_config, lang='en')

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

## Logging

By default only warnings and errors are shown. Pass `verbose=true` to enable INFO/DEBUG output, saved to `logs/evaluate_<timestamp>.log`:

```bash
patienthub evaluate verbose=true
```

## Integration with Simulations

Run a simulation to generate a session JSON, then evaluate it:

```bash
patienthub simulate \
  client=patientPsi \
  therapist=basic
```

```bash
patienthub evaluate \
  input_dir=data/sessions/default/session_1.json \
  output_dir=data/evaluations/session_1_conv.json \
  evaluator=conv_judge \
  evaluator.granularity=session
```

## Next Steps

- [Evaluators Reference](/docs/components/evaluators/overview) - Detailed evaluator documentation
- [Contributing: New Evaluators](/docs/contributing/new-evaluators) - Add custom evaluators
