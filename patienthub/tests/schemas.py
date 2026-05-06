"""
Schema validation tests for all client character data files.

Verifies that every entry in each character JSON file passes
model_validate() against its registered Pydantic schema.

Run with:
    python -m pytest patienthub/tests/schemas.py -v
or:
    python -m patienthub.tests.schemas
"""

import pytest

from patienthub.utils.files import load_json
from patienthub.schemas import CLIENT_SCHEMA_REGISTRY
from patienthub.clients import CLIENT_CONFIG_REGISTRY

SCHEMA_TEST_CASES = [
    (name, CLIENT_CONFIG_REGISTRY[name]().data_path, schema_cls)
    for name, schema_cls in CLIENT_SCHEMA_REGISTRY.items()
    if name != "user"
]


@pytest.mark.parametrize("agent_name,data_path,schema_cls", SCHEMA_TEST_CASES)
def test_all_entries_match_schema(agent_name, data_path, schema_cls):
    """Every entry in the character JSON validates against the registered schema."""
    entries = load_json(data_path)
    for i, entry in enumerate(entries):
        schema_cls.model_validate(entry), f"{agent_name}[{i}] failed validation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
