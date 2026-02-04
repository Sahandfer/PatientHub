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
  type: interviewer
  config:
    model: gpt-4o
    interview_type: intake
```

### In Code

```python
from patienthub.npcs import NPCRegistry

# Create an NPC
interviewer = NPCRegistry.create("interviewer", config={
    "model": "gpt-4o",
    "interview_type": "intake"
})

# Use the NPC in a simulation
response = interviewer.respond(conversation_history)
```

## Use Cases

### Family Therapy Simulation

```python
from patienthub.npcs import NPCRegistry
from patienthub.clients import ClientRegistry
from patienthub.therapists import TherapistRegistry

# Create agents
client = ClientRegistry.create("saps", config={...})
parent = NPCRegistry.create("family_member", config={
    "relationship": "parent",
    "personality": "concerned"
})
therapist = TherapistRegistry.create("cbt", config={...})

# Run family therapy simulation
# ...
```

### Social Skills Training

NPCs can role-play different social scenarios to help clients practice:

- Job interviews
- Difficult conversations
- Assertiveness training
- Conflict resolution

## Creating Custom NPCs

You can create custom NPCs to add new characters to your simulations:

```python
from patienthub.npcs.base import NPC

class FamilyMember(NPC):
    def __init__(self, config):
        super().__init__(config)
        self.relationship = config.get("relationship", "parent")
        self.personality = config.get("personality", "supportive")

    def respond(self, conversation_history):
        # Generate response based on relationship and personality
        return response
```

Then register it:

```python
from patienthub.npcs import NPCRegistry

NPCRegistry.register("family_member", FamilyMember)
```

## See Also

- [User Guide: Simulations](../../guide/simulations.md)
- [Creating Custom Agents](../../contributing/new-agents.md)
