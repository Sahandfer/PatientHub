# Profile Judge

`profile_judge` is the profile evaluator in PatientHub. It uses an LLM plus a prompt-defined schema to inspect a generated client profile and return structured results.

## Use Cases

- Evaluate whether generated client profiles are coherent and internally consistent
- Score profile quality with a prompt-defined rubric
- Extract specific profile issues or contradictions
- Benchmark different profile generators with the same evaluation schema

:::tip Notes
- `prompt_path` must be provided by configuration. `ProfileJudge` itself does not hard-code `client_profile.yaml`.
- Use a model that supports structured response schemas. The evaluator depends on structured output for `response_format`.
- Unsupported paradigms are skipped when building the schema.
- This evaluator is a good fit for judging profile quality before running a conversation simulation.
:::

## Overview

| Property           | Value |
| ------------------ | ----- |
| **Key**            | `profile_judge` |
| **Class**          | `patienthub.evaluators.profile.ProfileJudge` |
| **Base Class**     | `patienthub.evaluators.base.LLMJudge` |
| **Primary Input**  | A payload containing `profile` |
| **Prompt Source**  | `configs.prompt_path` |
| **Output Style**   | Prompt-driven structured JSON |

## How It Works

`profile_judge` is built on top of `LLMJudge`:

- `patienthub/evaluators/profile.py` validates that profile data exists.
- `patienthub/evaluators/base.py` loads the prompt, builds the schema, calls the model, and returns structured output.

At runtime, the evaluator:

1. Loads the YAML prompt from `prompt_path`
2. Reads `dimensions` from that YAML
3. Dynamically builds Pydantic response models for each dimension
4. Renders the prompt with Jinja2 using the provided `data`
5. Calls the chat model with `response_format=<dimension model>`
6. Returns one structured result per dimension

## Configuration

### Hydra Configuration

```yaml
defaults:
  - _self_
  - evaluator: profile_judge

evaluator:
  prompt_path: data/prompts/evaluator/client_profile.yaml
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
    "agent_type": "profile_judge",
    "prompt_path": "data/prompts/evaluator/client_profile.yaml",
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
  evaluator=profile_judge \
  evaluator.prompt_path=data/prompts/evaluator/client_profile.yaml \
  evaluator.model_type=OPENAI \
  evaluator.model_name=gpt-4o \
  input_dir=data/sessions/default/badtherapist.json \
  output_dir=data/evaluations/default/profile_judge_demo.json
```

## Prompt Structure

`profile_judge` does not hard-code a specific prompt file. Instead, it reads whatever YAML file you provide in `prompt_path`.

A minimal prompt looks like this:

```yaml
sys_prompt: |
  You are evaluating the quality of a generated client profile.

  ## Profile:
  {{data.profile}}

  Return the judgment in the required structured format.

dimensions:
  - name: consistency
    description: Whether the profile is internally consistent.
    paradigm: scalar
    range: [1, 5]
```

The bundled example prompt:

- `data/prompts/evaluator/client_profile.yaml`


## Supported Paradigms

Each dimension in the prompt must use one of the paradigms supported by `LLMJudge`:

| Paradigm | Returned Field | Example |
| -------- | -------------- | ------- |
| `binary` | `label: bool` | `{"label": true}` |
| `scalar` | `score: int` | `{"score": 4}` |
| `categorical` | `label: Literal[...]` | `{"label": "very consistent"}` |
| `extraction` | `snippets: List[str]` | `{"snippets": ["Profile: ..."]}` |

If `use_reasoning=true`, each leaf result also includes a `reasoning` field.

## Input Format

`profile_judge` expects a payload containing a `profile` object:

```json
{
  "profile": {
    "name": "Alex",
    "history": "Has anxiety around family events.",
    "situation": "Invited to a cousin's wedding.",
    "emotion": ["anxious", "sad"]
  }
}
```

## Output Format

The output shape is determined by your prompt's `dimensions`.

For the minimal prompt above, the result would look like:

```json
{
  "consistency": {
    "score": 4
  }
}
```

If `use_reasoning=true`, the leaf result includes a short explanation:

```json
{
  "consistency": {
    "score": 4,
    "reasoning": "The profile is mostly coherent and does not contain major internal contradictions."
  }
}
```

With the bundled prompt `data/prompts/evaluator/client_profile.yaml`, a typical result can contain multiple paradigms in one run:

```json
{
  "consistency_binary": {
    "label": true
  },
  "consistency_categorical": {
    "label": "very consistent"
  },
  "consistency_scalar": {
    "score": 4
  },
  "consistency_extraction": {
    "snippets": [
      "The profile consistently describes anxiety around family events."
    ]
  }
}
```

## See Also

- [Evaluators Overview](./overview.md)
- [Conv Judge](./conv_judge.md)
- [Evaluation Guide](../../guide/evaluation.md)
