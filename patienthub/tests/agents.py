"""
Registry tests shared by every agent type (clients, therapists, generators).

The client smoke tests build agents straight from CLIENT_REGISTRY, so they never
run get_client()/get_therapist()/get_generator(). These cover that path, where an
agent's declared language is looked up before construction.

Run with:
    python -m pytest patienthub/tests/agents.py -v
or:
    python -m patienthub.tests.agents
"""

import pytest
from unittest.mock import patch, MagicMock

from patienthub.clients import CLIENT_REGISTRY, CLIENT_DEFAULT_LANGS, get_client
from patienthub.generators import GENERATORS, GENERATOR_DEFAULT_LANGS, get_generator
from patienthub.therapists import (
    THERAPIST_REGISTRY,
    THERAPIST_DEFAULT_LANGS,
    get_therapist,
)

AGENT_KINDS = [
    ("client", get_client, CLIENT_REGISTRY, CLIENT_DEFAULT_LANGS),
    ("therapist", get_therapist, THERAPIST_REGISTRY, THERAPIST_DEFAULT_LANGS),
    ("generator", get_generator, GENERATORS, GENERATOR_DEFAULT_LANGS),
]
AGENT_IDS = [kind for kind, *_ in AGENT_KINDS]


@pytest.mark.parametrize("kind,getter,registry,langs", AGENT_KINDS, ids=AGENT_IDS)
def test_every_agent_declares_a_default_lang(kind, getter, registry, langs):
    """Every registry entry has a matching *_DEFAULT_LANGS entry."""
    assert set(registry) == set(langs), (
        f"{kind}: registry and DEFAULT_LANGS disagree — "
        f"missing={sorted(set(registry) - set(langs))}, "
        f"extra={sorted(set(langs) - set(registry))}"
    )


@pytest.mark.parametrize("kind,getter,registry,langs", AGENT_KINDS, ids=AGENT_IDS)
def test_getter_looks_up_the_declared_lang(kind, getter, registry, langs):
    """The getter passes the agent's own declared language to the warning."""
    agent_name = next(n for n, lang in langs.items() if lang is not None)
    seen = []
    # Stub the agent class so only the language lookup runs, not construction.
    with patch.dict(registry, {agent_name: MagicMock()}), patch(
        f"patienthub.{kind}s.language_warning",
        side_effect=lambda name, lang, default: seen.append((name, default)),
    ):
        getter(agent_name, lang="xx")
    assert seen == [(agent_name, langs[agent_name])]


# ===========================================================================
# Run directly: python -m patienthub.tests.agents
# ===========================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
