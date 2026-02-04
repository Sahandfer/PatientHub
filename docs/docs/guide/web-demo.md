---
sidebar_position: 4
---

# Web Demo

PatientHub includes a web-based demo using [Chainlit](https://chainlit.io/) for interactive patient simulation.

## Quick Start

```bash
chainlit run examples/chainlit.py
```

Open http://localhost:8000 in your browser.

## Features

- **Interactive Chat**: Chat with simulated patients in real-time
- **Patient Selection**: Switch between different patient types
- **Settings Panel**: Adjust temperature and other parameters
- **Session History**: View and export conversation history

## Configuration

The web demo uses settings that can be adjusted in the UI:

| Setting      | Description                     | Default      |
| ------------ | ------------------------------- | ------------ |
| Patient Type | Which patient simulation to use | `patientPsi` |
| Temperature  | Response randomness (0-1)       | `0.7`        |

## Custom Demo

Create a custom Chainlit app:

```python
# my_demo.py
import chainlit as cl
from omegaconf import OmegaConf
from patienthub.clients import get_client, CLIENT_REGISTRY

DEFAULT_CONFIG = {
    "agent_type": "patientPsi",
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 1024,
    "max_retries": 3,
    "data_path": "data/characters/PatientPsi.json",
    "data_idx": 0,
}


@cl.on_chat_start
async def start():
    # Create settings UI
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="client_type",
                label="Patient Type",
                values=list(CLIENT_REGISTRY.keys()),
                initial_value="patientPsi",
            ),
            cl.input_widget.Slider(
                id="temperature",
                label="Temperature",
                initial=0.7,
                min=0,
                max=1,
                step=0.1,
            ),
            cl.input_widget.Select(
                id="data_idx",
                label="Character",
                values=["0", "1", "2"],
                initial_value="0",
            ),
        ]
    ).send()

    await setup_client(settings)


async def setup_client(settings):
    config = DEFAULT_CONFIG.copy()
    config["agent_type"] = settings["client_type"]
    config["temperature"] = settings["temperature"]
    config["data_idx"] = int(settings["data_idx"])

    # Update data path based on client type
    client_type = settings["client_type"]
    config["data_path"] = f"data/characters/{client_type.title()}.json"

    configs = OmegaConf.create(config)

    try:
        client = get_client(configs=configs, lang="en")
        client.set_therapist({"name": "Therapist"})
        cl.user_session.set("client", client)

        await cl.Message(
            content=f"🧠 **Patient loaded:** `{client_type}`\n\n"
                    f"Character: {client.name}\n\n"
                    f"You are now the therapist. Start the conversation!"
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"⚠️ Error loading patient: {str(e)}"
        ).send()


@cl.on_settings_update
async def settings_update(settings):
    await setup_client(settings)


@cl.on_message
async def main(message: cl.Message):
    client = cl.user_session.get("client")

    if not client:
        await cl.Message(
            content="⚠️ No patient loaded. Please refresh the page."
        ).send()
        return

    # Show thinking indicator
    async with cl.Step(name="Generating response..."):
        response = client.generate_response(message.content)

    await cl.Message(
        content=response.content,
        author=client.name,
    ).send()


@cl.on_chat_end
async def end():
    client = cl.user_session.get("client")
    if client:
        client.reset()
```

Run:

```bash
chainlit run my_demo.py
```

## Adding Authentication

```python
# my_demo.py
import chainlit as cl

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if username == "researcher" and password == "demo123":
        return cl.User(identifier=username)
    return None
```

## Exporting Sessions

Add export functionality:

```python
import json

@cl.action_callback("export_session")
async def export_session(action):
    client = cl.user_session.get("client")

    if client and hasattr(client, 'messages'):
        session_data = {
            "client_type": client.configs.agent_type,
            "messages": [
                {"role": "user" if i % 2 == 0 else "assistant",
                 "content": str(msg.content)}
                for i, msg in enumerate(client.messages[1:])  # Skip system
            ]
        }

        # Create downloadable file
        elements = [
            cl.File(
                name="session.json",
                content=json.dumps(session_data, indent=2).encode(),
                display="inline",
            )
        ]

        await cl.Message(
            content="📥 Session exported!",
            elements=elements,
        ).send()
```

## Deployment

### Local Development

```bash
chainlit run app.py --host 0.0.0.0 --port 8000
```

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8000
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

Chainlit apps can be deployed to:

- **Chainlit Cloud**: `chainlit deploy`
- **Hugging Face Spaces**: Create a `Dockerfile` and push
- **Railway/Render**: Standard Python deployment

## Customization

### Custom Theme

Create `.chainlit/config.toml`:

```toml
[UI]
name = "PatientHub Demo"
description = "Interactive Patient Simulation"
default_theme = "light"

[UI.theme]
primary_color = "#2E8555"
```

### Custom CSS

Create `public/custom.css`:

```css
.message-author {
  font-weight: bold;
  color: #2e8555;
}
```

Reference in config:

```toml
[UI]
custom_css = "/public/custom.css"
```

## Next Steps

- [Chainlit Documentation](https://docs.chainlit.io/)
- [API Reference](/docs/api/clients) - Client configuration options
