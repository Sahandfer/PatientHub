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
    "agent_name": "conv_judge",
    "prompt_path": "data/prompts/evaluator/client_conv.yaml",
    "granularity": "session",
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
    "use_reasoning": False,
})

evaluator = get_evaluator(agent_name="conv_judge", configs=configs, lang="en")
results = evaluator.evaluate(session)
```

## Running Evaluations

### Command Line

```bash
patienthub evaluate \
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
    "agent_name": "conv_judge",
    "prompt_path": "data/prompts/evaluator/client_conv.yaml",
    "granularity": "session",
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
})

evaluator = get_evaluator(agent_name="conv_judge", configs=configs, lang="en")
results = []

for session_path in Path("outputs/").rglob("*.json"):
    session = load_json(str(session_path))
    result = evaluator.evaluate(session)
    results.append(result)
```

## Creating Custom Evaluators

You can create custom evaluators by extending the base judge class and pairing it with a config dataclass:

```python
from dataclasses import dataclass
from typing import Any, Dict

from patienthub.evaluators.base import LLMJudge, LLMJudgeConfig


@dataclass
class MyCustomEvaluatorConfig(LLMJudgeConfig):
    agent_name: str = "my_evaluator"
    prompt_path: str = "data/prompts/evaluator/my_evaluator.yaml"


class MyCustomEvaluator(LLMJudge):
    def evaluate(self, data: Dict[str, Any], *args) -> Dict[str, Any]:
        # Perform evaluation using the prompt-defined dimensions
        return self.evaluate_dimensions(data)
```

Then register both in the registries:

```python
# patienthub/evaluators/__init__.py
from .my_evaluator import MyCustomEvaluator, MyCustomEvaluatorConfig

EVALUATOR_REGISTRY["my_evaluator"] = MyCustomEvaluator
EVALUATOR_CONFIG_REGISTRY["my_evaluator"] = MyCustomEvaluatorConfig
```

## See Also

- [Creating Custom Evaluators](../../contributing/new-evaluators.md)
- [Evaluation Guide](../../guide/evaluation.md)
