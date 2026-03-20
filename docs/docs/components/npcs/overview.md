# NPCs (Non-Player Characters)

NPCs in PatientHub are supporting agents that can participate in therapy simulations beyond the primary client-therapist dyad.

## Available NPCs

| NPC                                 | Key           | Description                                 |
| ----------------------------------- | ------------- | ------------------------------------------- |
| [**Interviewer**](./interviewer.md) | `interviewer` | Conducts structured scripted interviews     |

## Usage

### In Code

```python
from omegaconf import OmegaConf
from patienthub.npcs.interviewer import InterviewerNPC

config = OmegaConf.create({"data": "data/evaluations/surveys/default_survey.json"})
interviewer = InterviewerNPC(configs=config)

question = interviewer.generate_response("start")
print(question)
```

## Use Cases

### Intake Interview (Before Therapy)

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client
from patienthub.therapists import get_therapist
from patienthub.npcs.interviewer import InterviewerNPC

# Create interviewer NPC (question script)
interviewer = InterviewerNPC(
    configs=OmegaConf.create({"data": "data/evaluations/surveys/default_survey.json"})
)

# Create client
client = get_client(agent_name="patientPsi", lang="en")

# Create therapist
therapist = get_therapist(agent_name="basic", lang="en")

# Run a quick intake, then start therapy
question = interviewer.generate_response("start")
print("Interviewer:", question)
answer = client.generate_response(question)
print("Client:", answer.content if hasattr(answer, "content") else answer)
```

## Creating Custom NPCs

To add a new NPC, create a new class under `patienthub/npcs/` and instantiate it directly. NPCs are lightweight — simply implement `generate_response()` and `reset()`.

```python
from omegaconf import DictConfig

class FamilyMemberNPC:
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.name = "Family Member"
        self.reset()

    def generate_response(self, msg: str):
        return "I'm here to support them."

    def reset(self):
        self.messages = []
```

## See Also

- [User Guide: Simulations](../../guide/simulations.md)
- [Creating Custom Agents](../../contributing/new-agents.md)
