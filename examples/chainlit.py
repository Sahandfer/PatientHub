"""
Chainlit-based web demo for PatientHub.

Run with: uv run chainlit run examples/chainlit.py
"""

import sys
import dataclasses
import chainlit as cl
from pathlib import Path
from omegaconf import OmegaConf

from patienthub.clients import get_client, CLIENT_REGISTRY, CLIENT_CONFIG_REGISTRY

# Ensure the project root is on sys.path so patienthub is importable
# even when Chainlit spawns its own process.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def get_client_options() -> list[str]:
    """Return client keys that work in a web UI."""
    return [k for k in CLIENT_REGISTRY if k != "user"]


def build_config(agent_type: str, overrides: dict | None = None) -> OmegaConf:
    config_cls = CLIENT_CONFIG_REGISTRY.get(agent_type)
    if config_cls is None:
        raise ValueError(f"Unknown client type: {agent_type}")

    config_dict = dataclasses.asdict(config_cls())
    if overrides:
        config_dict.update(overrides)

    return OmegaConf.create(config_dict)


@cl.on_chat_start
async def start():
    """Initialize the session with client selection."""
    client_options = get_client_options()

    settings = await cl.ChatSettings(
        [
            cl.input_widget.Select(
                id="client_type",
                label="Patient Type",
                values=client_options,
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
        ]
    ).send()

    await setup_client(settings)


async def setup_client(settings: dict):
    """Load a client agent from registry defaults + UI overrides."""
    agent_type = settings["client_type"]
    temperature = settings["temperature"]

    try:
        configs = build_config(agent_type, {"temperature": temperature})
        client = get_client(configs=configs, lang="en")
        client.set_therapist({"name": "Therapist"})
    except Exception as e:
        await cl.Message(
            content=f"Failed to load **{agent_type}** client: `{e}`"
        ).send()
        return

    cl.user_session.set("client", client)

    await cl.Message(
        content=(
            f"**Patient loaded:** `{agent_type}` — *{client.name}*\n\n"
            "You are the therapist. Start the conversation!\n\n"
            "*Tip: change settings in the sidebar to switch patients.*"
        ),
    ).send()


@cl.on_settings_update
async def settings_update(settings: dict):
    """Reset and reload when settings change."""
    prev_client = cl.user_session.get("client")
    if prev_client:
        prev_client.reset()

    await setup_client(settings)


@cl.on_message
async def main(message: cl.Message):
    """Handle therapist messages and generate patient responses."""
    client = cl.user_session.get("client")

    if not client:
        await cl.Message(content="No patient loaded. Please refresh the page.").send()
        return

    try:
        response = client.generate_response(message.content)
        # Some clients return a string, others return an object with .content
        text = response if isinstance(response, str) else response.content
    except Exception as e:
        await cl.Message(content=f"Error generating response: `{e}`").send()
        return

    await cl.Message(content=text, author=client.name).send()


@cl.on_chat_end
async def end():
    """Clean up on session end."""
    client = cl.user_session.get("client")
    if client:
        client.reset()
