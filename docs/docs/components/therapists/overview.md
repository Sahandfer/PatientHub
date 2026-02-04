# Therapists

Therapist agents in PatientHub provide the therapeutic interventions during simulated conversations. They can range from sophisticated AI-powered therapists to simple rule-based systems, enabling various research and training scenarios.

## Available Therapists

| Therapist                     | Key     | Description                                                                         |
| ----------------------------- | ------- | ----------------------------------------------------------------------------------- |
| [**CBT Therapist**](./cbt.md) | `cbt`   | A Cognitive Behavioral Therapy therapist that employs evidence-based CBT techniques |
| [**Eliza**](./eliza.md)       | `eliza` | Classic pattern-matching therapist based on the original ELIZA program              |
| [**Bad Therapist**](./bad.md) | `bad`   | A deliberately poor therapist for training purposes                                 |
| [**User**](./user.md)         | `user`  | Human-in-the-loop therapist for interactive sessions                                |

## Usage

### In Configuration

```yaml
therapist:
  key: cbt
  config:
    model: gpt-4o
```

### In Code

```python
from patienthub.therapists import TherapistRegistry

# Get available therapists
available = TherapistRegistry.list()

# Create a therapist
therapist = TherapistRegistry.create("cbt", config={"model": "gpt-4o"})
```

## CBT Therapist

The CBT (Cognitive Behavioral Therapy) therapist implements evidence-based CBT techniques including:

- **Cognitive restructuring** - Identifying and challenging negative thought patterns
- **Behavioral activation** - Encouraging engagement in positive activities
- **Problem-solving** - Helping clients develop coping strategies
- **Psychoeducation** - Explaining the connection between thoughts, feelings, and behaviors

### Configuration

```yaml
therapist:
  key: cbt
  config:
    model: gpt-4o
    temperature: 0.7
```

## Eliza

ELIZA is a classic pattern-matching conversational agent originally developed at MIT. This implementation provides a nostalgic but functional therapist that:

- Uses pattern matching to generate responses
- Reflects statements back to the client
- Asks open-ended questions
- Provides unconditional positive regard

### Configuration

```yaml
therapist:
  key: eliza
```

## Bad Therapist

The bad therapist is intentionally designed to demonstrate poor therapeutic practices. Useful for:

- Training mental health professionals to recognize bad practices
- Testing client agent robustness
- Research on therapeutic alliance

### Configuration

```yaml
therapist:
  key: bad
  config:
    model: gpt-4o
```

## User (Human-in-the-Loop)

The user therapist enables human participation in therapy simulations, useful for:

- Training scenarios
- Evaluation studies
- Interactive demonstrations

### Configuration

```yaml
therapist:
  key: user
```

## Creating Custom Therapists

You can create custom therapists by extending the base `Therapist` class:

```python
from patienthub.therapists.base import Therapist

class MyCustomTherapist(Therapist):
    def __init__(self, config):
        super().__init__(config)
        # Initialize your therapist

    def respond(self, conversation_history):
        # Generate therapeutic response
        return response
```

Then register it:

```python
from patienthub.therapists import TherapistRegistry

TherapistRegistry.register("my_therapist", MyCustomTherapist)
```

## See Also

- [Creating Custom Therapists](../../contributing/new-agents.md)
