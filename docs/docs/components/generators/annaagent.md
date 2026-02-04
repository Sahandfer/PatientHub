# AnnaAgent Generator

The AnnaAgent Generator creates character files specifically designed for the AnnaAgent client method, which supports multi-session counseling with dynamic memory evolution.

## Overview

| Property   | Value                     |
| ---------- | ------------------------- |
| **Key**    | `annaAgent`               |
| **Type**   | LLM-based                 |
| **Output** | AnnaAgent character files |

## Description

The AnnaAgent Generator produces detailed character specifications that are compatible with the AnnaAgent client method. It creates profiles with rich backstories, presenting problems, and memory structures that can evolve across multiple therapy sessions.

## Key Features

- **Multi-session Support** - Generates characters designed for longitudinal therapy
- **Memory Evolution** - Creates initial memory states that can dynamically update
- **Rich Backstories** - Detailed personal histories and context
- **Session Goals** - Defines therapeutic objectives for each character

## Configuration

### YAML Configuration

```yaml
generator:
  type: annaAgent
  config:
    model: gpt-4o
    temperature: 0.8
    include_memory_structure: true
```

### Python Usage

```python
from patienthub.generators import GeneratorRegistry

generator = GeneratorRegistry.create("annaAgent", config={
    "model": "gpt-4o",
    "temperature": 0.8
})

character = generator.generate({
    "disorder": "depression",
    "severity": "moderate",
    "session_count": 5
})
```

## Parameters

| Parameter                  | Type   | Default  | Description                           |
| -------------------------- | ------ | -------- | ------------------------------------- |
| `model`                    | string | `gpt-4o` | The LLM model to use                  |
| `temperature`              | float  | `0.8`    | Controls creativity in generation     |
| `include_memory_structure` | bool   | `true`   | Include dynamic memory initialization |

## Output Format

```json
{
  "name": "Sarah",
  "age": 28,
  "background": "Software engineer dealing with work-related stress...",
  "presenting_problem": "Difficulty sleeping, persistent sadness...",
  "memory": {
    "core_beliefs": ["I'm not good enough"],
    "recent_events": [...],
    "therapeutic_progress": []
  },
  "session_goals": [...]
}
```

## Use Cases

- Creating diverse client pools for multi-session research
- Generating training data for AnnaAgent clients
- Building character libraries for educational purposes
