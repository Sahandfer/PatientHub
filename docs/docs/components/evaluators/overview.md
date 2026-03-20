# Evaluators

Evaluators in PatientHub assess the quality of therapy simulations, providing automated metrics and analysis of conversations between client and therapist agents.
Currently, we only support `LLM as Judge` style evaluators, which use large language models to evaluate conversations or generated profiles based on specific criteria.

## Available Evaluators

| Evaluator                                       | Key             | Description            |
| ----------------------------------------------- | --------------- | ---------------------- |
| [**LLM Judge (Conversation)**](./conv_judge.md) | `conv_judge`    | Conversation Evaluator |
| [**LLM Judge (Profile)**](./profile_judge.md)   | `profile_judge` | Profile Evaluator      |

## Usage

### In Configuration

```yaml
defaults:
  - _self_
  - evaluator: conv_judge

evaluator:
  prompt_path: data/prompts/evaluator/client_conv.yaml
  granularity: session
  model_type: OPENAI
  model_name: gpt-4o
  use_reasoning: false
```

### In Code

```python
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator
from patienthub.utils import load_json

session = load_json("data/sessions/default/badtherapist.json")

configs = OmegaConf.create({
    "agent_type": "conv_judge",
    "prompt_path": "data/prompts/evaluator/client_conv.yaml",
    "granularity": "session",
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
    "use_reasoning": False,
})

evaluator = get_evaluator(configs=configs, lang="en")
results = evaluator.evaluate(session)
```

## Running Evaluations

### Command Line

```bash
uv run python -m examples.evaluate \
    evaluator=conv_judge \
    evaluator.prompt_path=data/prompts/evaluator/client_conv.yaml \
    evaluator.granularity=session \
    evaluator.model_type=OPENAI \
    evaluator.model_name=gpt-4o \
    input_dir=data/sessions/default/badtherapist.json
```

### Batch Evaluation

```python
from pathlib import Path
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator
from patienthub.utils import load_json

configs = OmegaConf.create({
    "agent_type": "conv_judge",
    "prompt_path": "data/prompts/evaluator/client_conv.yaml",
    "granularity": "session",
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
})

evaluator = get_evaluator(configs=configs, lang="en")
results = []

for session_path in Path("outputs/").rglob("*.json"):
    session = load_json(str(session_path))
    result = evaluator.evaluate(session)
    results.append(result)
```

## Creating Custom Evaluators

You can create custom evaluators by extending the base judge class:

```python
from patienthub.evaluators.base import LLMJudge

class MyCustomEvaluator(LLMJudge):
    def __init__(self, configs):
        super().__init__(configs)
        # Initialize your evaluator

    def evaluate(self, data):
        # Perform evaluation
        return self.evaluate_dimensions(data)
```

Then register it:

```python
# patienthub/evaluators/__init__.py
from .my_evaluator import MyCustomEvaluator, MyCustomEvaluatorConfig

EVALUATOR_REGISTRY["my_evaluator"] = MyCustomEvaluator
EVALUATOR_CONFIG_REGISTRY["my_evaluator"] = MyCustomEvaluatorConfig
```

## See Also

- [Creating Custom Evaluators](../../contributing/new-evaluators.md)
- [Evaluation Guide](../../guide/evaluation.md)
