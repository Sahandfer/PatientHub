# Therapists

Therapist agents in PatientHub provide the therapeutic interventions during simulated conversations. They can range from sophisticated AI-powered therapists to simple rule-based systems, enabling various research and training scenarios.

## Available Therapists

| Therapist                     | Key     | Description                                                                         |
| ----------------------------- | ------- | ----------------------------------------------------------------------------------- |
| [**MI Therapist**](./cami.md) | `cami`   | A Counselor Agent Supporting Motivational Interviewing through State Inference and Topic Exploration |
| [**CBT Therapist**](./psyche.md) | `psyche`   | A psychiatrist agent simulated using a structured prompt with explicit clinical assessment criteria. |
| [**CBT Therapist**](./cbt.md) | `CBT`   | A Cognitive Behavioral Therapy therapist that employs evidence-based CBT techniques |
| [**Eliza**](./eliza.md)       | `eliza` | Classic pattern-matching therapist based on the original ELIZA program              |
| [**Bad Therapist**](./bad.md) | `bad`   | A deliberately poor therapist for training purposes                                 |
| [**User**](./user.md)         | `user`  | Human-in-the-loop therapist for interactive sessions |      

- Prompt Data is stored in `data/prompts/therapist`.

## Usage

### Listing Available Therapists

```python
from patienthub.therapists import THERAPIST_CONFIG_REGISTRY, THERAPIST_REGISTRY

# List all therapist types
print("Available therapists:", list(THERAPIST_REGISTRY.keys()))

# Get config class for a therapist
config_class = THERAPIST_CONFIG_REGISTRY['cami']
print(config_class)
```

### Loading a Therapist

```python
from omegaconf import OmegaConf

from patienthub.therapists import THERAPIST_REGISTRY, CBTTherapistConfig, get_therapist

# Get available therapists
available = list(THERAPIST_REGISTRY.keys())

# Create a therapist
cfg = OmegaConf.structured(CBTTherapistConfig(model_name="gpt-4o"))
therapist = get_therapist(cfg, lang="en")
```

## Creating Custom Therapists

You can create custom therapists by running the following command:

```bash
uv run python -m examples.create generator.gen_agent_type=tberapist generator.gen_agent_name=<agent_name>
```

This creates:

- `patienthub/therapists/<agent_name>.py`
- `data/prompts/therapist/<agent_name>.yaml`

You can also create custom therapists by extending the base `Therapist` class:

```python
from dataclasses import dataclass
from omegaconf import DictConfig

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import get_chat_model, load_prompts


@dataclass
class MyCustomTherapistConfig(APIModelConfig):
    agent_type: str = "my_therapist"


class MyCustomTherapist(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.name = "My Custom Therapist"
        self.chat_model = get_chat_model(configs)
        self.reset()

    def set_client(self, client, prev_sessions=None):
        self.client = client.get("name", "client")

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages).content
        self.messages.append({"role": "assistant", "content": res})
        return res

    def reset(self):
        self.messages = [{"role": "system", "content": "You are a helpful therapist."}]
        self.client = None
```

Then register it:

```python
from patienthub.therapists import THERAPIST_CONFIG_REGISTRY, THERAPIST_REGISTRY

THERAPIST_REGISTRY["my_therapist"] = MyCustomTherapist
THERAPIST_CONFIG_REGISTRY["my_therapist"] = MyCustomTherapistConfig
```

## See Also

- [Creating Custom Therapists](../../contributing/new-agents.md)
