---
sidebar_position: 2
---

# Batch Processing

Run multiple simulations for research experiments and benchmarking.

## Basic Usage

```bash
uv run python -m examples.batch_simulate \
  --clients patientPsi,consistentMI \
  --therapists CBT \
  --num_runs 10
```

## Command Line Options

| Option          | Description                     | Default                     |
| --------------- | ------------------------------- | --------------------------- |
| `--clients`     | Comma-separated client types    | `patientPsi`                |
| `--therapists`  | Comma-separated therapist types | `CBT`                       |
| `--num_runs`    | Runs per combination            | `5`                         |
| `--max_turns`   | Max turns per session           | `20`                        |
| `--max_workers` | Parallel workers                | `4`                         |
| `--output_dir`  | Output directory                | `outputs/batch/<timestamp>` |
| `--seed`        | Random seed for reproducibility | `None`                      |
| `--config`      | YAML config file                | `None`                      |

## Using a Config File

Create `batch_config.yaml`:

```yaml
clients:
  - patientPsi
  - consistentMI
  - eeyore
therapists:
  - CBT
  - MI
num_runs: 10
max_turns: 25
max_workers: 8
seed: 42
model_type: LAB
model_name: gpt-4o
temperature: 0.7
```

Run:

```bash
uv run python -m examples.batch_simulate --config batch_config.yaml
```

## Output Structure

```
outputs/batch/2026-01-19_14-30-00/
├── patientPsi_CBT_run0.json
├── patientPsi_CBT_run1.json
├── patientPsi_CBT_run2.json
├── ...
├── consistentMI_MI_run9.json
└── batch_summary.json
```

### Summary File

`batch_summary.json` contains aggregate statistics:

```json
{
  "total_runs": 60,
  "successful": 58,
  "failed": 2,
  "by_combination": {
    "patientPsi_CBT": {
      "num_runs": 10,
      "avg_turns": 18.5,
      "std_turns": 3.2
    },
    "consistentMI_MI": {
      "num_runs": 10,
      "avg_turns": 22.1,
      "std_turns": 4.8
    }
  }
}
```

## Export Results

Convert to CSV for analysis:

```bash
# Session-level export
uv run python -m examples.export \
  --input_dir outputs/batch/2026-01-19_14-30-00 \
  --output results.csv \
  --stats

# Turn-level export
uv run python -m examples.export \
  --input_dir outputs/batch/2026-01-19_14-30-00 \
  --output messages.csv \
  --level turn
```

### Session CSV Format

| Column            | Description                  |
| ----------------- | ---------------------------- |
| `source_file`     | Path to source JSON          |
| `patient_name`    | Patient character name       |
| `num_turns`       | Number of conversation turns |
| `total_messages`  | Total message count          |
| `therapist_words` | Word count from therapist    |
| `client_words`    | Word count from client       |

### Turn CSV Format

| Column         | Description             |
| -------------- | ----------------------- |
| `session_file` | Path to source JSON     |
| `turn_idx`     | Turn index (0-based)    |
| `role`         | `therapist` or `client` |
| `content`      | Message content         |
| `word_count`   | Words in message        |

## Python API

```python
from examples.batch_simulate import BatchConfig, run_batch, aggregate_results

config = BatchConfig(
    clients=['patientPsi', 'consistentMI'],
    therapists=['CBT'],
    num_runs=5,
    max_turns=20,
    max_workers=4,
    seed=42,
)

results = run_batch(config)
summary = aggregate_results(results, config.output_dir)

print(f"Completed: {summary['successful']}/{summary['total_runs']}")
```

## Analysis with Pandas

```python
import pandas as pd
from patienthub.utils.export import sessions_to_dataframe, load_sessions

# Load and convert
sessions = load_sessions('outputs/batch/2026-01-19_14-30-00')
df = sessions_to_dataframe(sessions)

# Analyze
print(df.describe())
print(df.groupby('patient_name').mean())

# Plot
import matplotlib.pyplot as plt
df.boxplot(column='num_turns', by='patient_name')
plt.savefig('turns_comparison.png')
```

## Reproducibility

For reproducible experiments:

```yaml
# batch_config.yaml
seed: 42
model_type: LAB
model_name: gpt-4o
temperature: 0.0 # Deterministic
```

:::tip
Set `temperature: 0.0` for deterministic outputs, though this may reduce response diversity.
:::

## Parallel Processing

Adjust workers based on API rate limits:

```bash
# Conservative (avoid rate limits)
uv run python -m examples.batch_simulate --max_workers 2

# Aggressive (fast local models)
uv run python -m examples.batch_simulate --max_workers 16
```

## Error Handling

Failed runs are logged but don't stop the batch:

```json
{
  "status": "error",
  "client": "patientPsi",
  "therapist": "CBT",
  "run_id": 3,
  "error": "API rate limit exceeded"
}
```

Check failed runs:

```python
import json

with open('outputs/batch/2026-01-19/batch_summary.json') as f:
    summary = json.load(f)

print(f"Failed: {summary['failed']}/{summary['total_runs']}")
```

## Next Steps

- [Evaluation](/docs/guide/evaluation) - Assess conversation quality
- [API Reference](/docs/api/clients) - Detailed configuration options
