---
sidebar_position: 3
---

# Evaluators API

Evaluators assess the quality of simulated conversations.

## Available Evaluators

| Evaluator | Description                       | Config Class             |
| --------- | --------------------------------- | ------------------------ |
| `rating`  | Score conversations on dimensions | `RatingEvaluatorConfig`  |
| `inspect` | Identify specific issues          | `InspectEvaluatorConfig` |

## Loading an Evaluator

```python
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator

config = OmegaConf.create({
    'eval_type': 'rating',
    'target': 'client',
    'dimensions': ['consistency', 'emotion'],
    'granularity': 'session',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_retries': 3,
})

evaluator = get_evaluator(configs=config, lang='en')
```

## Evaluator Interface

```python
class EvaluatorAgent(ABC):
    configs: DictConfig
    model: Any
    lang: str

    @abstractmethod
    def generate(
        self,
        prompt: str,
        response_format: Optional[Type[BaseModel]] = None,
    ) -> BaseModel | str:
        """Generate evaluation based on input."""
        pass

    @abstractmethod
    def evaluate(self, data: Any, *args) -> Dict[str, Any]:
        """Evaluate the provided data."""
        pass
```

## Rating Evaluator

Scores conversations on multiple dimensions with numeric ratings.

### Configuration

```python
config = OmegaConf.create({
    'eval_type': 'rating',
    'target': 'client',           # 'client' or 'therapist'
    'dimensions': ['consistency', 'emotion'],
    'granularity': 'session',     # 'session', 'turn', or 'turn_by_turn'
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.3,           # Lower for more consistent ratings
    'max_tokens': 1024,
    'max_retries': 3,
})
```

### Usage

```python
from patienthub.utils import load_json

# Load session data
session = load_json('data/sessions/default/session.json')

# Evaluate
evaluator = get_evaluator(configs=config, lang='en')
results = evaluator.evaluate(session)

print(results)
```

### Output Format

```json
{
  "consistency": {
    "character_adherence": {
      "score": 8,
      "comments": "The patient maintained consistent personality traits throughout."
    },
    "factual_consistency": {
      "score": 9,
      "comments": "No contradictions in stated facts or history."
    },
    "overall_score": 8
  },
  "emotion": {
    "authenticity": {
      "score": 7,
      "comments": "Emotional responses felt genuine but occasionally flat."
    },
    "appropriateness": {
      "score": 8,
      "comments": "Emotions were appropriate to the context."
    },
    "overall_score": 7
  }
}
```

## Inspect Evaluator

Identifies specific issues without numeric scores.

### Configuration

```python
config = OmegaConf.create({
    'eval_type': 'inspect',
    'target': 'client',
    'dimensions': ['consistency'],
    'granularity': 'turn_by_turn',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 1024,
    'max_retries': 3,
})
```

### Output Format

```json
{
  "consistency": {
    "character_adherence": {
      "issues": [
        "Turn 5: Patient suddenly became very talkative, contradicting earlier established introverted personality.",
        "Turn 12: Patient mentioned having siblings after stating they were an only child in Turn 3."
      ],
      "comments": [
        "The personality shift was abrupt and unexplained.",
        "Direct factual contradiction about family structure."
      ]
    }
  }
}
```

## Evaluation Dimensions

### Client Dimensions

| Dimension     | Description            | Aspects                                      |
| ------------- | ---------------------- | -------------------------------------------- |
| `consistency` | Character consistency  | `character_adherence`, `factual_consistency` |
| `emotion`     | Emotional authenticity | `authenticity`, `appropriateness`            |
| `resistance`  | Natural resistance     | `engagement_level`, `defense_mechanisms`     |

### Therapist Dimensions

| Dimension          | Description            | Aspects                                         |
| ------------------ | ---------------------- | ----------------------------------------------- |
| `cbt`              | CBT technique usage    | `cognitive_techniques`, `behavioral_techniques` |
| `active_listening` | Listening skills       | `reflection`, `summarization`, `clarification`  |
| `pedagogical`      | Teaching effectiveness | `psychoeducation`, `skill_building`             |

## Granularity Options

### Session-Level

Evaluate the entire conversation at once:

```python
config['granularity'] = 'session'
```

### Turn-Level

Evaluate only the last turn:

```python
config['granularity'] = 'turn'
```

### Turn-by-Turn

Evaluate each turn individually:

```python
config['granularity'] = 'turn_by_turn'

results = evaluator.evaluate(session)
# Returns: {"turn_0": {...}, "turn_2": {...}, "turn_4": {...}, ...}
```

## Input Data Format

Evaluators expect data in this format:

```python
data = {
    "profile": {
        "demographics": {"name": "Alex", "age": 28},
        "presenting_problem": "...",
        # ... other character data
    },
    "messages": [
        {"role": "therapist", "content": "Hello, how are you?"},
        {"role": "client", "content": "I've been feeling anxious..."},
        {"role": "therapist", "content": "Can you tell me more?"},
        {"role": "client", "content": "Well, it started when..."},
    ]
}
```

## Batch Evaluation

```python
from pathlib import Path
from patienthub.utils import load_json, save_json

input_dir = Path('outputs/batch/2026-01-19')
results = {}

for session_file in input_dir.glob('*.json'):
    if session_file.name == 'batch_summary.json':
        continue

    session = load_json(str(session_file))
    eval_result = evaluator.evaluate(session)
    results[session_file.stem] = eval_result

save_json(results, 'outputs/evaluations/batch_eval.json')
```

## Custom Dimensions

Create custom dimensions in `patienthub/evaluators/dimensions/`:

```python
# patienthub/evaluators/dimensions/therapeutic_alliance.py
from .base import Dimension, Aspect

THERAPEUTIC_ALLIANCE = Dimension(
    name="therapeutic_alliance",
    description="Quality of the therapeutic relationship",
    aspects=[
        Aspect(
            name="rapport",
            description="Level of connection and trust between therapist and client",
            guidelines="Look for warmth, empathy, and mutual understanding.",
        ),
        Aspect(
            name="collaboration",
            description="Degree of collaborative goal-setting and problem-solving",
            guidelines="Check if both parties contribute to the conversation direction.",
        ),
    ],
    target="therapist",  # or "client"
)
```

Register in `__init__.py`:

```python
from .therapeutic_alliance import THERAPEUTIC_ALLIANCE

DIMENSION_REGISTRY = {
    # ... existing dimensions
    "therapeutic_alliance": THERAPEUTIC_ALLIANCE,
}
```

Use:

```python
config['dimensions'] = ['therapeutic_alliance']
```

## Aggregating Results

```python
import statistics

# Load evaluation results
with open('outputs/evaluations/batch_eval.json') as f:
    evaluations = json.load(f)

# Extract scores
consistency_scores = []
for session_name, result in evaluations.items():
    if 'consistency' in result:
        consistency_scores.append(result['consistency']['overall_score'])

# Compute statistics
print(f"Mean: {statistics.mean(consistency_scores):.2f}")
print(f"Std: {statistics.stdev(consistency_scores):.2f}")
print(f"Range: {min(consistency_scores)} - {max(consistency_scores)}")
```
