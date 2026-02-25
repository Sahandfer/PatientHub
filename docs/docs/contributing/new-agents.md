---
sidebar_position: 1
---

# Adding New Patient Agents

This guide explains how to add new patient/client simulation methods to PatientHub.

## Overview

Patient agents implement different simulation approaches. Each method typically comes from a research paper and has unique characteristics for modeling patient behavior.

## Architecture

```
patienthub/clients/
├── __init__.py          # Agent registry
├── basic.py             # Base class
├── patientPsi.py        # Example implementation
├── consistentMI.py      # Another example
└── your_new_agent.py    # Your new agent
```

## Step 1: Create Agent File

Create a new file in `patienthub/clients/`:

```python
# patienthub/clients/myAgent.py

from typing import Any, Optional
from langchain_core.messages import AIMessage, HumanMessage

from patienthub.base.agents import BaseAgent
from patienthub.brain.profile import PatientProfile


class MyAgent(BaseAgent):
    """
    Implement your patient simulation method.

    Paper: Your Paper Title
    Venue: Conference Year
    """

    def __init__(
        self,
        configs: Any,
        lang: str = "en",
        **kwargs
    ):
        super().__init__(configs=configs, lang=lang, **kwargs)

        # Load your character data
        self._load_character()

        # Initialize any method-specific state
        self.internal_state = {}

    def _load_character(self):
        """Load character from data file."""
        import json
        with open(self.configs.data_path, 'r') as f:
            characters = json.load(f)

        self.character = characters[self.configs.data_idx]

        # Parse into profile if needed
        self.profile = PatientProfile.from_dict(self.character)

    def _build_system_prompt(self) -> str:
        """Construct the system prompt for your method."""
        prompt = f"""You are simulating a patient named {self.character['name']}.

Background:
{self.character.get('background', 'No background provided.')}

Presenting Problem:
{self.character.get('presenting_problem', 'No presenting problem specified.')}

Your role is to respond as this patient would in a therapy session.
Maintain consistency with the character description.
"""
        # Add method-specific instructions
        if 'special_instructions' in self.character:
            prompt += f"\n\nSpecial Instructions:\n{self.character['special_instructions']}"

        return prompt

    def generate_response(
        self,
        message: str,
        **kwargs
    ) -> AIMessage:
        """
        Generate a patient response to therapist input.

        Args:
            message: The therapist's message
            **kwargs: Additional parameters

        Returns:
            AIMessage containing the patient's response
        """
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
        ]

        # Add conversation history
        for msg in self.conversation_history:
            messages.append({
                "role": "assistant" if isinstance(msg, AIMessage) else "user",
                "content": msg.content
            })

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call LLM
        response = self.llm.invoke(messages)

        # Update internal state (method-specific)
        self._update_state(message, response.content)

        # Store in history
        self.conversation_history.append(HumanMessage(content=message))
        self.conversation_history.append(AIMessage(content=response.content))

        return AIMessage(content=response.content)

    def _update_state(self, therapist_msg: str, patient_response: str):
        """Update internal state based on interaction."""
        # Implement your method's state update logic
        pass

    def get_state(self) -> dict:
        """Return current internal state for evaluation."""
        return {
            "profile": self.profile.to_dict() if self.profile else {},
            "internal_state": self.internal_state,
            "turn_count": len(self.conversation_history) // 2,
        }

    def reset(self):
        """Reset agent state for new session."""
        self.conversation_history = []
        self.internal_state = {}
```

## Step 2: Register the Agent

Add your agent to the registry in `patienthub/clients/__init__.py`:

```python
from patienthub.clients.myAgent import MyAgent

CLIENT_REGISTRY = {
    # ... existing agents ...
    'myAgent': MyAgent,
}

def get_client(configs, lang: str = "en", **kwargs):
    agent_type = configs.agent_type
    if agent_type not in CLIENT_REGISTRY:
        raise ValueError(f"Unknown client type: {agent_type}")
    return CLIENT_REGISTRY[agent_type](configs=configs, lang=lang, **kwargs)
```

## Step 3: Create Character Data

Add character data in `data/characters/`:

```json
// data/characters/MyAgent.json
[
  {
    "name": "Taylor",
    "age": 29,
    "gender": "non-binary",
    "occupation": "graphic designer",
    "background": "Recently moved to a new city for work...",
    "presenting_problem": "Experiencing social anxiety...",
    "personality": {
      "traits": ["introverted", "creative", "sensitive"],
      "communication_style": "thoughtful, sometimes hesitant"
    },
    "special_instructions": "Tends to pause before answering difficult questions"
  }
]
```

## Step 4: Create Configuration

Add a Hydra config in `data/characters/` or reference via CLI:

```yaml
# Can be used as: client=myAgent
agent_type: myAgent
model_type: OPENAI
model_name: gpt-4o
temperature: 0.7
max_tokens: 1024
max_retries: 3
data_path: data/characters/MyAgent.json
data_idx: 0
```

## Step 5: Add Tests

Create tests in `patienthub/tests/`:

```python
# patienthub/tests/test_myAgent.py

import pytest
from omegaconf import OmegaConf
from patienthub.clients import get_client


@pytest.fixture
def agent_config():
    return OmegaConf.create({
        'agent_type': 'myAgent',
        'model_type': 'OPENAI',
        'model_name': 'gpt-4o-mini',
        'temperature': 0.0,  # Deterministic for tests
        'max_tokens': 256,
        'max_retries': 3,
        'data_path': 'data/characters/MyAgent.json',
        'data_idx': 0,
    })


def test_agent_initialization(agent_config):
    """Test that agent initializes correctly."""
    agent = get_client(configs=agent_config, lang='en')
    assert agent is not None
    assert agent.character['name'] == 'Taylor'


def test_agent_response(agent_config):
    """Test that agent generates valid responses."""
    agent = get_client(configs=agent_config, lang='en')
    response = agent.generate_response("Hello, how are you today?")
    assert response is not None
    assert len(response.content) > 0


def test_agent_conversation(agent_config):
    """Test multi-turn conversation."""
    agent = get_client(configs=agent_config, lang='en')

    r1 = agent.generate_response("What brings you in today?")
    r2 = agent.generate_response("Tell me more about that.")

    # Should maintain conversation history
    assert len(agent.conversation_history) == 4  # 2 turns x 2 messages
```

## Step 6: Add Documentation

Create a doc page in `docs/docs/components/`:

```markdown
---
sidebar_position: N
---

# MyAgent

> Paper Title Here

**Venue**: Conference Year

## Overview

Brief description of your method.

## Key Features

- Feature 1
- Feature 2

## Usage

\`\`\`bash
uv run python -m examples.simulate client=myAgent
\`\`\`

...
```

## Advanced Features

### Implementing State Transitions

```python
class StatefulAgent(BaseAgent):
    STATES = ['initial', 'engaged', 'resistant', 'resolved']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_state = 'initial'

    def _update_state(self, therapist_msg: str, patient_response: str):
        # Analyze interaction and potentially transition
        if self._detect_engagement(therapist_msg):
            self.current_state = 'engaged'
        # ... more logic
```

### Adding Memory/Multi-session Support

```python
class MemoryAgent(BaseAgent):
    def save_session(self, path: str):
        """Save session for multi-session support."""
        import json
        with open(path, 'w') as f:
            json.dump({
                'history': [m.content for m in self.conversation_history],
                'state': self.internal_state,
            }, f)

    def load_session(self, path: str):
        """Load previous session."""
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        # Restore state...
```

## Checklist

Before submitting your new agent:

- [ ] Agent class in `patienthub/clients/`
- [ ] Registered in `__init__.py`
- [ ] Character data file created
- [ ] Unit tests passing
- [ ] Documentation page added
- [ ] Example usage works: `python -m examples.simulate client=yourAgent`
