# Generators

Generators in PatientHub create synthetic client profiles, therapy scenarios, and conversation data for training and research purposes.

## Overview

Generators enable the automatic creation of:

- **Client Profiles** - Synthetic patient backgrounds and presenting problems
- **Therapy Scenarios** - Structured situations for simulation
- **Conversation Data** - Training data for AI models
- **Character Files** - Complete character specifications for client agents

## Available Generators

| Generator                | Description                                   |
| ------------------------ | --------------------------------------------- |
| **AnnaAgent Generator**  | Creates character files for AnnaAgent clients |
| **ClientCast Generator** | Generates diverse client characters           |
| **Psyche Generator**     | Creates psychologically rich client profiles  |

## Usage

### Command Line

```bash
python examples/generate.py \
    --generator annaAgent \
    --output outputs/characters/
```

### In Code

```python
from patienthub.generators import GeneratorRegistry

# Create a generator
generator = GeneratorRegistry.create("annaAgent", config={
    "model": "gpt-4o"
})

# Generate a client profile
profile = generator.generate({
    "disorder": "depression",
    "severity": "moderate"
})
```

## Generation Types

### Client Profile Generation

Create detailed client backgrounds including:

- Demographics
- Presenting problems
- History and background
- Personality traits
- Communication style

```python
profile = generator.generate_profile({
    "disorder": "anxiety",
    "age_range": "25-35",
    "gender": "any",
    "background": "professional"
})
```

### Character File Generation

Generate complete character specification files:

```python
character = generator.generate_character({
    "profile": profile,
    "format": "json",
    "include_dialogue_examples": True
})
```

### Scenario Generation

Create therapy scenarios:

```python
scenario = generator.generate_scenario({
    "type": "initial_session",
    "client_profile": profile,
    "therapeutic_approach": "CBT"
})
```

## Configuration

### Generator Settings

```yaml
generator:
  type: annaAgent
  config:
    model: gpt-4o
    temperature: 0.8
    diversity: high
    output_format: json
```

### Output Formats

Generators support multiple output formats:

- **JSON** - Structured data for programmatic use
- **YAML** - Human-readable configuration files
- **Markdown** - Documentation-friendly format

## Batch Generation

Generate multiple profiles at once:

```python
from patienthub.generators import GeneratorRegistry

generator = GeneratorRegistry.create("clientCast")

# Generate 10 diverse profiles
profiles = generator.batch_generate(
    count=10,
    diversity_constraints={
        "disorders": ["depression", "anxiety", "ptsd"],
        "age_range": [18, 65],
        "balance_gender": True
    }
)
```

## Creating Custom Generators

You can create custom generators:

```python
from patienthub.generators.base import Generator

class MyCustomGenerator(Generator):
    def __init__(self, config):
        super().__init__(config)
        # Initialize your generator

    def generate(self, params):
        # Generate content
        return generated_content
```

Then register it:

```python
from patienthub.generators import GeneratorRegistry

GeneratorRegistry.register("my_generator", MyCustomGenerator)
```

## Best Practices

1. **Diversity** - Ensure generated profiles represent diverse populations
2. **Realism** - Validate generated content against clinical knowledge
3. **Ethics** - Review generated content for appropriateness
4. **Versioning** - Track generated content versions for reproducibility

## See Also

- [API Reference: Clients](../api/clients.md)
- [Creating Custom Agents](../contributing/new-agents.md)
