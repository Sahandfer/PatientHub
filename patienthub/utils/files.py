import os
import json
import yaml
from jinja2 import Template


def load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def parse_json_response(res):
    try:
        res = res.replace("```json", "").replace("```", "")
        res = json.loads(res)
        return res
    except Exception as e:
        print(f"Error while parsing JSON response: {e}")
        return res


def save_json(data, output_dir: str, overwrite: bool = False):
    # Check if the directory exists, if not create it
    if not os.path.exists(os.path.dirname(output_dir)):
        os.makedirs(os.path.dirname(output_dir))

    if overwrite or not os.path.exists(output_dir):
        with open(output_dir, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    else:
        prev_data = None
        with open(output_dir, "r", encoding="utf-8") as f:
            prev_data = json.load(f)

        if isinstance(prev_data, list):
            prev_data.append(data)
        elif prev_data:
            prev_data = [prev_data, data]
        else:
            prev_data = [data]

        with open(output_dir, "w", encoding="utf-8") as f:
            json.dump(prev_data, f, indent=4, ensure_ascii=False)


def load_yaml(path: str):
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print("Error loading YAML file:", e)
        return {}


def load_prompts(role: str, agent_type: str, lang: str = "en"):
    path = f"data/prompts/{role}/{agent_type}.yaml"
    prompts = {}
    data = load_yaml(path)[lang]
    for k, v in data.items():
        if isinstance(v, str):
            prompts[k] = Template(v)
    return prompts
