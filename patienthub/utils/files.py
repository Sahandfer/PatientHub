import os
import json
import yaml
import pandas as pd
from jinja2 import Template


def load_csv(path: str):
    return pd.read_csv(path)


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
    parent_dir = os.path.dirname(output_dir)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

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
        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print("Error loading YAML file:", e)
        return {}


def process_prompts(data):
    if isinstance(data, str):
        return Template(data)
    elif isinstance(data, dict):
        return {k: process_prompts(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [process_prompts(item) for item in data]
    else:
        print(f"Unsupported data type in prompts: {type(data)}")
        return None


def load_prompts(path: str, lang: str = "en"):
    try:
        data = load_yaml(path)
        if lang in data:
            data = data[lang]

        return process_prompts(data)
    except Exception as e:
        print(f"Error loading prompts from {path}: {e}")
        return {}
