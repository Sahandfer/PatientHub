# Evaluators

Evaluators in PatientHub assess the quality of therapy simulations, providing automated metrics and analysis of conversations between client and therapist agents.

## Available Evaluators

| Evaluator                       | Key         | Description                                             |
| ------------------------------- | ----------- | ------------------------------------------------------- |
| [**LLM Judge**](./llm-judge.md) | `llm_judge` | Uses large language models to evaluate therapy sessions |

## Usage

### In Configuration

```yaml
evaluator:
  key: llm_judge
  config:
    model: gpt-4o
    criteria:
      - empathy
      - adherence
      - effectiveness
```

### In Code

```python
from patienthub.evaluators import EvaluatorRegistry

# List available evaluators
available = EvaluatorRegistry.list()

# Create an evaluator
evaluator = EvaluatorRegistry.create("llm_judge", config={
    "model": "gpt-4o"
})

# Evaluate a conversation
results = evaluator.evaluate(conversation_history)
```

## Running Evaluations

### Command Line

```bash
# Evaluate with defaults
uv run python -m examples.evaluate

# Override evaluator and paths
uv run python -m examples.evaluate \
    evaluator=llm_judge \
    input_dir=data/sessions/session.json
```

### Batch Evaluation

```python
from patienthub.evaluators import EvaluatorRegistry

evaluator = EvaluatorRegistry.create("llm_judge")

sessions = load_sessions("outputs/")
results = []

for session in sessions:
    result = evaluator.evaluate(session)
    results.append(result)
```

## Creating Custom Evaluators

You can create custom evaluators by extending the base class:

```python
from patienthub.evaluators.base import Evaluator

class MyCustomEvaluator(Evaluator):
    def __init__(self, config):
        super().__init__(config)
        # Initialize your evaluator

    def evaluate(self, conversation_history):
        # Perform evaluation
        return {
            "score": score,
            "feedback": feedback
        }
```

Then register it:

```python
from patienthub.evaluators import EvaluatorRegistry

EvaluatorRegistry.register("my_evaluator", MyCustomEvaluator)
```

## See Also

- [Creating Custom Evaluators](../../contributing/new-evaluators.md)
- [Evaluation Guide](../../guide/evaluation.md)
