from jinja2 import Template
import yaml


def get_prompts(agent_type):
    prompts = {}
    with open(f"src/prompts/{agent_type}.yaml", "r") as file:
        prompts = yaml.safe_load(file)
    for k, v in prompts.items():
        if isinstance(v, str):
            prompts[k] = Template(v)
    return prompts
