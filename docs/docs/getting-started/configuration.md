---
sidebar_position: 3
---

# Configuration

PatientHub uses [Hydra](https://hydra.cc/) for configuration management, making it easy to override settings from the command line or config files.

## Environment Variables

Create a `.env` file in the project root:

```bash
# For OPENAI API (default)
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com

# For HuggingFace
HF_TOKEN=your_huggingface_token
```

## Model Configuration

### Using OPENAI API (Default)

```python
config = {
    'model_type': 'OPENAI',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
}
```

### Using OpenAI

```python
config = {
    'model_type': 'openai',
    'model_name': 'gpt-4-turbo',
    'temperature': 0.7,
    'max_tokens': 1024,
}
```

### Using HuggingFace

```python
config = {
    'model_type': 'huggingface',
    'model_name': 'meta-llama/Llama-2-7b-chat-hf',
    'device': 0,  # GPU device index
    'max_new_tokens': 512,
    'temperature': 0.7,
    'repetition_penalty': 1.1,
}
```

### Using Local Models

```python
config = {
    'model_type': 'local',
    'model_name': 'path/to/your/model',
    'device': 0,
    'max_new_tokens': 512,
    'temperature': 0.7,
}
```

## Client Configuration

### Common Options

| Option        | Type  | Default    | Description             |
| ------------- | ----- | ---------- | ----------------------- |
| `agent_type`  | str   | required   | Client type identifier  |
| `model_type`  | str   | `"OPENAI"`    | Model provider          |
| `model_name`  | str   | `"gpt-4o"` | Model identifier        |
| `temperature` | float | `0.7`      | Sampling temperature    |
| `max_tokens`  | int   | `1024`     | Max response tokens     |
| `max_retries` | int   | `3`        | API retry attempts      |
| `data_path`   | str   | varies     | Path to character JSON  |
| `data_idx`    | int   | `0`        | Index in character file |
| `lang`        | str   | `"en"`     | Language code           |

### Client-Specific Options

#### ConsistentMI

```yaml
client:
  agent_type: consistentMI
  initial_stage: precontemplation # precontemplation, contemplation, preparation, action
```

#### SimPatient

```yaml
client:
  agent_type: simPatient
  continue_last_session: false
  conv_history_path: data/sessions/SimPatient/session_1.json
```

## Session Configuration

```yaml
event:
  event_type: therapySession
  max_turns: 30
  reminder_turn_num: 5
  output_dir: data/sessions/default/session_1.json
```

## Evaluation Configuration

```yaml
evaluator:
  agent_type: llm_judge
  eval_type: scalar # classification | scalar | binary | extraction
  target: client # client or therapist
  instruction_dir: data/prompts/evaluator/client/scalar.yaml
  granularity: session # session | turn | turn_by_turn
  use_reasoning: false
```

## Command Line Overrides

Override any config value from the command line:

```bash
# Single override
uv run python -m examples.simulate client.temperature=0.5

# Multiple overrides
uv run python -m examples.simulate \
  client=patientPsi \
  client.temperature=0.5 \
  therapist=CBT \
  event.max_turns=50

# Override nested values
uv run python -m examples.simulate client.data_idx=2
```

## Config Files

Create custom config files in the appropriate directories:

### Custom Client Config

Create `configs/client/myclient.yaml`:

```yaml
agent_type: patientPsi
model_type: OPENAI
model_name: gpt-4o
temperature: 0.5
max_tokens: 2048
data_path: data/characters/PatientPsi.json
data_idx: 0
```

Use it:

```bash
uv run python -m examples.simulate client=myclient
```

## Debugging

Enable debug output:

```bash
# Show full config
uv run python -m examples.simulate --cfg job

# Show config sources
uv run python -m examples.simulate --info
```
