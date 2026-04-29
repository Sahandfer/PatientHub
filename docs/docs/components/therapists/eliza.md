# Eliza

ELIZA is a classic rule-based conversational agent originally developed at MIT in the 1960s, providing a pattern-matching Rogerian therapist baseline.

## Overview

| Property  | Value            |
| --------- | ---------------- |
| **Key**   | `eliza`          |
| **Type**  | Rule-based       |
| **Focus** | Rogerian Therapy |

## Key Features

- **Pattern matching**: Uses regex patterns to generate contextual responses
- **Reflection**: Reflects client statements back as questions
- **Open-ended questions**: Encourages elaboration without leading
- **No LLM required**: Fully deterministic, no API key needed

## How It Works

ELIZA implements the classic DOCTOR script. On each turn it scans the input for matching patterns (e.g. "I feel X" → "Why do you feel X?"), applies a reflection transform, and falls back to generic prompts when no pattern matches.

## Usage

### CLI

```bash
patienthub simulate therapist=eliza
```

### Python

```python
from patienthub.therapists import get_therapist

therapist = get_therapist(agent_name="eliza", lang='en')

response = therapist.generate_response("I feel very anxious.")
print(response)
```

## Configuration

ELIZA uses a fixed rule-based system and does not require any configuration parameters.

## Use Cases

- Baseline comparisons with LLM-based therapists
- Historical/educational demonstrations of early conversational AI
- Low-resource environments where LLM access is unavailable
- Research on rule-based vs. LLM therapeutic interaction
