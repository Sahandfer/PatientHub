from jinja2 import Environment, FileSystemLoader


def get_prompt(agent_type, agent_name):
    try:
        env = Environment(loader=FileSystemLoader(f"src/prompts/{agent_type}"))
        return env.get_template(f"{agent_name}.j2")
    except Exception as e:
        print(f"Error while loading prompt: {e}")
