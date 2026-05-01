"""
Smoke tests for all client agents.

Verifies that each client can:
  1. Load its character/data JSON file
  2. Load its prompt YAML templates
  3. Instantiate without errors (with a mocked chat model)
  4. Build a non-empty system prompt / initial messages list
  5. Accept a therapist via set_therapist()
  6. Reset cleanly (if the method exists)

Run with:
    python -m pytest patienthub/tests/clients.py -v
or:
    python -m patienthub.tests.clients
"""

import pytest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from omegaconf import OmegaConf

from patienthub.clients import CLIENT_REGISTRY, CLIENT_CONFIG_REGISTRY
from patienthub.schemas import CLIENT_SCHEMA_REGISTRY

# ---------------------------------------------------------------------------
# Helper: mock get_chat_model so tests never hit a real API
# Patch where it's *used* (base.py) not where it's *defined*, so the local
# reference in base.py is replaced and ChatModel.__init__ is never called.
# ---------------------------------------------------------------------------
MOCK_CHAT_MODEL_PATH = "patienthub.clients.base.get_chat_model"


def _mock_chat_model(_configs=None):
    model = MagicMock()
    model.generate.return_value = MagicMock(content="mock response")
    model.get_usage.return_value = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
    }
    return model


# clientCast loads two extra JSON files in __init__; mock them to avoid I/O
def _mock_clientcast_load_json(path):
    if "human_data" in path:
        return [{"messages": [{"role": "user", "content": "Hello"}]}]
    if "symptoms" in path:
        return {}
    return []


EXTRA_PATCHES = {
    "clientCast": [
        ("patienthub.clients.clientCast.load_json", _mock_clientcast_load_json)
    ],
}

DUMMY_THERAPIST = SimpleNamespace(name="Dr. Test")

# All clients except "user" (requires stdin)
ALL_CLIENTS = [name for name in CLIENT_REGISTRY if name != "user"]


# ---------------------------------------------------------------------------
# Fixture: instantiate any client by name with a mocked LLM
# ---------------------------------------------------------------------------
@pytest.fixture(params=ALL_CLIENTS)
def client(request):
    agent_name = request.param
    patches = [(MOCK_CHAT_MODEL_PATH, _mock_chat_model)]
    for path, fn in EXTRA_PATCHES.get(agent_name, []):
        patches.append((path, fn))
    with ExitStack() as stack:
        for path, fn in patches:
            stack.enter_context(patch(path, side_effect=fn))
        cfg = OmegaConf.structured(CLIENT_CONFIG_REGISTRY[agent_name])
        yield CLIENT_REGISTRY[agent_name](configs=cfg)


# ===========================================================================
# Shared tests — run once per client automatically
# ===========================================================================


def test_instantiation(client):
    """Client __init__ completes without error."""
    assert client is not None



def test_data_loaded(client):
    """Client loaded its character/data file."""
    assert hasattr(client, "data") and client.data is not None


def test_prompts_loaded(client):
    """Client loaded its prompt templates."""
    assert hasattr(client, "prompts") and client.prompts and len(client.prompts) > 0


def test_messages_initialized(client):
    """Client has at least one system message after init (if it uses messages)."""
    if not hasattr(client, "messages"):
        pytest.skip("Client does not use a messages list")
    if not client.messages:
        pytest.skip("Client builds messages lazily (requires set_therapist first)")
    assert client.messages[0]["role"] == "system"
    assert len(client.messages[0]["content"]) > 0


def test_set_therapist(client):
    """set_therapist() stores the therapist name."""
    client.set_therapist(DUMMY_THERAPIST)
    assert hasattr(client, "therapist")
    assert isinstance(client.therapist, str) and len(client.therapist) > 0


def test_reset(client):
    """reset() clears therapist and rebuilds state (if implemented)."""
    if not hasattr(client, "reset"):
        pytest.skip("Client does not implement reset()")
    client.set_therapist(DUMMY_THERAPIST)
    client.reset()
    # After reset, therapist should be cleared
    assert client.therapist is None


# Clients that use multi-step structured LLM calls — hard to mock simply
SKIP_GENERATE_RESPONSE = {"saps", "consistentMI", "adaptiveVP"}


def test_generate_response(client, request):
    """generate_response() runs and returns a result with content."""
    if request.node.callspec.id in SKIP_GENERATE_RESPONSE:
        pytest.skip("Multi-step structured LLM flow; skipped in smoke tests")
    client.set_therapist(DUMMY_THERAPIST)
    res = client.generate_response("How have you been feeling lately?")
    content = res.content if hasattr(res, "content") else res
    assert isinstance(content, str) and len(content) > 0


# ===========================================================================
# Registry completeness
# ===========================================================================


@pytest.mark.parametrize("agent_name", ALL_CLIENTS)
def test_registry_has_both_entries(agent_name):
    """Every client has entries in both CLIENT_REGISTRY and CLIENT_CONFIG_REGISTRY."""
    assert agent_name in CLIENT_REGISTRY, f"{agent_name} missing from CLIENT_REGISTRY"
    assert (
        agent_name in CLIENT_CONFIG_REGISTRY
    ), f"{agent_name} missing from CLIENT_CONFIG_REGISTRY"
    assert (
        agent_name in CLIENT_SCHEMA_REGISTRY
    ), f"{agent_name} missing from CLIENT_SCHEMA_REGISTRY"


# ===========================================================================
# Run directly: python -m patienthub.tests.clients
# ===========================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
