from typing import Any, Dict, List


def flatten_dict(item_dict: Dict[str, Any]):
    """Flatten a nested dictionary into a single-level dictionary."""
    flat_dict = {}
    for key, value in item_dict.items():
        if isinstance(value, dict):
            nested_flat = flatten_dict(value)
            for nested_key, nested_value in nested_flat.items():
                flat_dict[f"{key}_{nested_key}"] = nested_value
        else:
            flat_dict[key] = value
    return flat_dict


def dict_to_str(d: Dict[str, Any], indent: int = 0, prefix: str = "") -> str:
    """Convert a dictionary to a formatted string."""
    lines = []
    for key, value in d.items():
        line = " " * indent + f"{prefix}" + f"{key}: "
        if isinstance(value, dict):
            lines.append(line)
            lines.append(dict_to_str(value, indent + 2, prefix + f"{key}_"))
        elif isinstance(value, list):
            lines.append(line)
            for i, item in enumerate(value):
                lines.append(" " * (indent + 2) + f"- {item}")
        else:
            lines.append(line + str(value))
    return "\n".join(lines)


def flatten_conv(
    messages: List[Dict[str, str]], roles: Dict[str, str] = None, max_turns: int = None
) -> str:
    """Convert conversation history into a single string."""
    messages = [
        msg
        for msg in messages
        if msg.get("content", "").strip() and msg.get("role") != "system"
    ]
    if max_turns is not None:
        messages = messages[-max_turns * 2 :]
    if roles is None:
        return "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages
        )
    else:
        return "\n".join(
            f"{roles.get(msg['role'], msg['role']).capitalize()}: {msg['content']}"
            for msg in messages
        )
