# Eliza

ELIZA is a classic pattern-matching conversational agent originally developed at MIT, providing a nostalgic but functional therapist implementation.

## Overview

| Property  | Value            |
| --------- | ---------------- |
| **Key**   | `eliza`          |
| **Type**  | Rule-based       |
| **Focus** | Rogerian Therapy |

## Description

ELIZA was one of the first chatbots, created by Joseph Weizenbaum at MIT in the 1960s. This implementation recreates the classic DOCTOR script, which simulates a Rogerian psychotherapist. Despite its simplicity, ELIZA demonstrates how pattern matching can create surprisingly engaging conversations.

## Key Features

- **Pattern matching** - Uses regex patterns to generate contextual responses
- **Reflection** - Reflects statements back to the client
- **Open-ended questions** - Asks questions that encourage elaboration
- **Unconditional positive regard** - Maintains a supportive, non-judgmental tone

## Configuration

### YAML Configuration

```yaml
therapist:
  key: eliza
```

### Python Usage

```python
from patienthub.therapists import TherapistRegistry

therapist = TherapistRegistry.create("eliza")
```

## Parameters

ELIZA uses a fixed rule-based system and does not require additional configuration parameters.

## Use Cases

- Baseline comparisons with LLM-based therapists
- Historical/educational demonstrations
- Low-resource environments where LLM access is unavailable
- Research on human-computer interaction
