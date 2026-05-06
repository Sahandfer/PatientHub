# Conv Judge

`conv_judge` is the conversation evaluator in PatientHub. It uses an LLM plus a prompt-defined schema to score or inspect a therapy session and return structured results.

## Use Cases

- Evaluate standardized-patient consistency across a full session
- Run prompt-defined inspection tasks such as contradiction extraction
- Benchmark different client simulators with the same rubric

:::tip Notes
- `prompt_path` must be provided by configuration. `ConvJudge` itself does not hard-code `client_conv.yaml`.
- Use a model that supports structured response schemas. The evaluator depends on structured output for `response_format`.
:::

## Overview

| Property           | Value |
| ------------------ | ----- |
| **Key**            | `conv_judge` |
| **Class**          | `patienthub.evaluators.conv.ConvJudge` |
| **Base Class**     | `patienthub.evaluators.base.LLMJudge` |
| **Primary Input**  | A session-like payload containing `messages` |
| **Prompt Source**  | `configs.prompt_path` |
| **Modes**   | `session`, `turn`, `turn_by_turn` |
| **Output Style**   | Prompt-driven structured JSON |

## How It Works

`conv_judge` is split across two files:

- `patienthub/evaluators/conv.py` prepares conversation data.
- `patienthub/evaluators/base.py` loads the prompt, builds the schema, calls the model, and returns structured output.

At runtime, the evaluator:

1. Loads the YAML prompt from `prompt_path`
2. Reads `dimensions` from that YAML
3. Dynamically builds Pydantic response models for each dimension
4. Formats the conversation according to `granularity`
5. Renders the prompt with Jinja2
6. Calls the chat model with `response_format=<dimension model>`
7. Returns one structured result per dimension

## Configuration

### Hydra Configuration

```yaml
defaults:
  - _self_
  - evaluator: conv_judge

evaluator:
  prompt_path: data/prompts/evaluator/client_conv.yaml
  granularity: session
  use_reasoning: false
  model_type: OPENAI
  model_name: gpt-4o
```

### Python Usage

```python
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator
from patienthub.utils import load_json

session = load_json("data/sessions/default/badtherapist.json")

configs = OmegaConf.create({
    "agent_type": "conv_judge",
    "prompt_path": "data/prompts/evaluator/client_conv.yaml",
    "granularity": "session",
    "use_reasoning": False,
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
})

evaluator = get_evaluator(configs=configs, lang="en")
results = evaluator.evaluate(session)
print(results)
```

### Command Line

```bash
patienthub evaluate \
  evaluator=conv_judge \
  evaluator.prompt_path=data/prompts/evaluator/client_conv.yaml \
  evaluator.granularity=session \
  evaluator.model_type=OPENAI \
  evaluator.model_name=gpt-4o \
  input_dir=data/sessions/default/badtherapist.json \
  output_dir=data/evaluations/default/conv_judge_demo.json
```

## Prompt Structure

`conv_judge` does not hard-code a specific prompt file. Instead, it reads whatever YAML file you provide in `prompt_path`.

A minimal prompt looks like this:

```yaml
sys_prompt: |
  You are evaluating a client in a therapy conversation.

  ## Conversation History:
  {{data.conv_history}}

  {% if data.last_response %}
  ## Latest Client Response:
  {{data.last_response}}
  {% endif %}

  Return the judgment in the required structured format.

dimensions:
  - name: consistency
    description: Whether the client is consistent across the conversation.
    paradigm: scalar
    range: [1, 5]
    aspects:
      - name: conv_factual
        description: Whether the client contradicts themselves across turns
```

The bundled example prompt:

- `data/prompts/evaluator/client_conv.yaml`

## Supported Paradigms

Each dimension in the prompt must use one of the paradigms supported by `LLMJudge`:

| Paradigm | Returned Field | Example |
| -------- | -------------- | ------- |
| `binary` | `label: bool` | `{"label": true}` |
| `scalar` | `score: int` | `{"score": 4}` |
| `categorical` | `label: Literal[...]` | `{"label": "very consistent"}` |
| `extraction` | `snippets: List[str]` | `{"snippets": ["Client: ..."]}` |

If `use_reasoning=true`, each leaf result also includes a `reasoning` field.

## Input Format

`conv_judge` expects a session-like object with a `messages` field:

```json
{
  "profile": { }, //(optional)
  "messages": [
    {"role": "therapist", "content": "How are you feeling today?"},
    {"role": "client", "content": "I have been anxious lately."},
    {"role": "therapist", "content": "When did it start?"},
    {"role": "client", "content": "About two months ago."}
  ]
}
```

Behavior by granularity:

- `session`: evaluates the entire flattened conversation
- `turn`: evaluates only the last response, while still providing prior context

## Output Format

The output shape is determined by your prompt's `dimensions`.

For the minimal prompt above, the result would look like:

```json
{
  "consistency": {
    "conv_factual": {
      "score": 4
    }
  }
}
```

If `use_reasoning=true`, the leaf result includes a short explanation:

```json
{
  "consistency": {
    "conv_factual": {
      "score": 4,
      "reasoning": "The client is mostly consistent and does not show major contradictions."
    }
  }
}
```

With a richer prompt such as `data/prompts/evaluator/client_conv.yaml`, you can define multiple dimensions and paradigms in the same evaluation run.

## See Also

- [Evaluators Overview](./overview.md)
- [Profile Judge](./profile_judge.md)
- [Evaluation Guide](../../guide/evaluation.md)
