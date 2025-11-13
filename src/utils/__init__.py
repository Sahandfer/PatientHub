import os
import json
import yaml
from jinja2 import Template
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv(".env")


def load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def load_yaml(path: str):
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Prompt loading error: {e}")
        return {}


def load_prompts(role: str, agent_type: str, lang: str):
    prompts = {}
    path = f"data/prompts/{role}/{agent_type}_{lang}.yaml"
    data = load_yaml(path)
    for k, v in data.items():
        if isinstance(v, str):
            prompts[k] = Template(v)
    return prompts


def parse_json_response(res):
    try:
        res = res.replace("```json", "").replace("```", "")
        res = json.loads(res)
        return res
    except Exception as e:
        print(f"Error while parsing JSON response: {e}")
        return res


def save_json(data, file_path: str):
    # Checck if the directory exists, if not create it
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_model_client(model_name: str, api_type: str = "OR"):
    configs = {"temperature": 0.4, "max_tokens": 8192, "max_retries": 3}
    return init_chat_model(
        model=model_name,
        model_provider="openai",
        base_url=os.environ.get(f"{api_type}_BASE_URL"),
        api_key=os.environ.get(f"{api_type}_API_KEY"),
        temperature=configs["temperature"],
        max_tokens=configs["max_tokens"],
        max_retries=configs["max_retries"],
    )
