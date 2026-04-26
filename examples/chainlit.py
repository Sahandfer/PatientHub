"""
Chainlit-based web demo for PatientHub.

Run with: uv run chainlit run examples/chainlit.py
"""

import sys
import chainlit as cl
from pathlib import Path

# Ensure the project root is on sys.path so patienthub is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from patienthub.clients import get_client, CLIENT_REGISTRY


def get_client_options() -> list[str]:
    """Return client keys that work in a web UI."""
    return [k for k in CLIENT_REGISTRY if k != "user"]


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
            )
        ]
    ).send()

    await setup_client(settings["client_type"])


async def setup_client(agent_name: str):
    """Load a client agent from registry defaults + UI overrides."""
    try:
        client = get_client(agent_name=agent_name, lang="en")
    except Exception as e:
        await cl.Message(
            content=f"Failed to load **{agent_name}** client: `{e}`"
        ).send()
        return

    cl.user_session.set("client", client)

    await cl.Message(
        content=(
            f"**Patient loaded:** `{agent_name}` — *{client.name}*\n\n"
            "You are the therapist. Start the conversation!\n\n"
            "*Tip: change settings in the sidebar to switch patients.*"
        ),
    ).send()


@cl.on_settings_update
async def settings_update(settings):
    """Reset and reload when settings change."""
    prev_client = cl.user_session.get("client")
    if prev_client:
        prev_client.reset()
    print()

    await setup_client(settings["client_type"])


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
