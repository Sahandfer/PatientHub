import json


def parse_json_response(res):
    try:
        res = res.replace("```json", "").replace("```", "")
        res = json.loads(res)
        return res
    except json.JSONDecodeError:
        return res


def to_bullet_list(data):
    res = ""

    # If it's a list
    if isinstance(data, list):
        res += "\n".join([f"- {item}" for item in data])
    # If it's a dict
    elif isinstance(data, dict):
        for k, v in data.items():
            res += f"- {k.capitalize()}: {v}\n"
    else:
        print("Invalid data type for to_bullet_list")

    return res
