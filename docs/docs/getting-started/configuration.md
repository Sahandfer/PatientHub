---
sidebar_position: 3
---

# Configuration

PatientHub uses [Hydra](https://hydra.cc/) for configuration management, making it easy to override settings from the command line or config files.

## Environment Variables

Create a `.env` file in the project root:

```bash
{model_type}_API_KEY=api_key_for_the_service
{model_type}_BASE_URL=base_url_for_the_service
```

For example,

```bash
# For OpenAI (default)
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com

# For local OpenAI-compatible servers (model_type = LOCAL)
LOCAL_BASE_URL=http://127.0.0.1:8000/v1
LOCAL_API_KEY=EMPTY
```

`model_type` is used to select the environment-variable namespace. For example, `model_type=LOCAL` makes PatientHub read `LOCAL_BASE_URL` and `LOCAL_API_KEY`.

## Data Layout

PatientHub keeps generator data in three directories under `data/`:

| Directory          | Contents                                                                                                                            |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| `data/seeds/`      | Per-character generation inputs. A `generate` run reads `data/seeds/<generator>.json` (a JSON list) via `input_path`; one seed record produces one character. |
| `data/resources/`  | Shared reference knowledge a method consults during generation (event databases, symptom item definitions, disease priors, etc.). Configured per generator (e.g. `resource_dir`) or shared as importable constants in `patienthub.resources`, not per character. |
| `data/characters/` | Generated outputs. The `generate` CLI writes results here (defaults to `data/characters/<generator>.json`).                        |

## Model Configuration

### Using OpenAI (Default)

```python
config = {
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
}
```

## Client Configuration

### Common Options

| Option        | Type  | Default    | Description             |
| ------------- | ----- | ---------- | ----------------------- |
| `agent_name`  | str   | required   | Agent type identifier   |
| `model_type`  | str   | `"OPENAI"` | Model provider          |
| `model_name`  | str   | `"gpt-4o"` | Model identifier        |
| `temperature` | float | `0.7`      | Sampling temperature    |
| `max_tokens`  | int   | `8192`     | Max response tokens     |
| `max_retries` | int   | `3`        | API retry attempts      |
| `prompt_path` | str   | varies     | Path to method Prompt   |
| `data_path`   | str   | varies     | Path to character JSON  |
| `data_idx`    | int   | `0`        | Index in character file |
| `lang`        | str   | `"en"`     | Language                |

### Client-Specific Options

#### ConsistentMI

```yaml
client:
  agent_name: consistentMI
  model_type: OPENAI
  model_name: gpt-4o
  reranker_model_type: LOCAL
  reranker_model_name: hosted_vllm/BAAI/bge-reranker-v2-m3
```

`ConsistentMI` uses the main `model_type` / `model_name` pair for response generation and a separate `reranker_model_type` / `reranker_model_name` pair for topic matching. The reranker currently reuses `LOCAL_BASE_URL` and `LOCAL_API_KEY`.

#### SimPatient

```yaml
client:
  agent_name: simPatient
  continue_last_session: false
  conv_history_path: data/sessions/SimPatient/session_1.json
```

## Session Configuration

```yaml
event:
  event_type: therapy_session
  max_turns: 15
  reminder_turn_num: 2
  output_dir: data/sessions/default/session_1.json
```

## Evaluation Configuration

```yaml
evaluator:
  agent_name: conv_judge # conv_judge | profile_judge
  prompt_path: data/prompts/evaluator/client_conv.yaml
  granularity: session # session | turn | turn_by_turn (conv_judge only)
  use_reasoning: false
```

## Command Line Overrides

Override any config value from the command line:

```bash
# Single override
patienthub simulate client.temperature=0.5

# Multiple overrides
patienthub simulate \
  client=patientPsi \
  client.temperature=0.5 \
  therapist=basic \
  event.max_turns=50

# Override nested values
patienthub simulate client.data_idx=2
```

## Config Files

Create custom config files in the appropriate directories:

### Custom Client Config

Create `configs/client/myClient.yaml`:

```yaml
agent_name: myClient
model_type: OPENAI
model_name: gpt-4o
temperature: 0.5
max_tokens: 2048
prompt_path: data/prompts/client/patientPsi.yaml
data_path: data/characters/patientPsi.json
data_idx: 0
```

Use it:

```bash
patienthub simulate client=myClient
```
