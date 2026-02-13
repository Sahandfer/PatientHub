# NPCs (Non-Player Characters)

NPCs in PatientHub are supporting agents that can participate in therapy simulations beyond the primary client-therapist dyad. These agents can represent family members, friends, or other individuals relevant to the client's situation.

## Overview

NPCs enable more realistic and complex therapy scenarios by introducing additional perspectives and dynamics. They can be used to:

- Simulate family therapy sessions
- Role-play social situations the client finds challenging
- Practice communication skills with different personality types
- Create more immersive therapeutic environments

## Available NPCs

| NPC                                 | Key           | Description                                 |
| ----------------------------------- | ------------- | ------------------------------------------- |
| [**Interviewer**](./interviewer.md) | `interviewer` | Conducts structured interviews with clients |

## Usage

### In Configuration

```yaml
npc:
  agent_type: interviewer
  data: data/evaluations/surveys/default_survey.json
```

### In Code

```python
from omegaconf import OmegaConf

from patienthub.npcs.interviewer import InterviewerNPC

config = OmegaConf.create({"data": "data/evaluations/surveys/default_survey.json"})
interviewer = InterviewerNPC(configs=config)

next_question = interviewer.generate_response("start")
print(next_question)
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
client_config = OmegaConf.create(
    {
        "agent_type": "saps",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 8192,
        "max_retries": 3,
        "data_path": "data/characters/SAPS.json",
        "data_idx": 0,
    }
)
client = get_client(configs=client_config, lang="en")

# Create therapist
therapist_config = OmegaConf.create(
    {
        "agent_type": "CBT",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 8192,
        "max_retries": 3,
    }
)
therapist = get_therapist(configs=therapist_config, lang="en")

# Run a quick intake, then start therapy
question = interviewer.generate_response("start")
print("Interviewer:", question)
answer = client.generate_response(question)
print("Client:", answer.content if hasattr(answer, "content") else answer)
```

### Social Skills Training

NPCs can role-play different social scenarios to help clients practice:

- Job interviews
- Difficult conversations
- Assertiveness training
- Conflict resolution

## Creating Custom NPCs

To add a new NPC, create a new `ChatAgent` implementation under `patienthub/npcs/`
(similar to `InterviewerNPC`) and instantiate it directly.

```python
from omegaconf import DictConfig

from patienthub.base import ChatAgent

class FamilyMemberNPC(ChatAgent):
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
