import yaml


def get_configs(config_name):
    file_path = f"src/config/{config_name}.yaml"
    with open(file_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(f"Error loading YAML file for {file_path}: {e}")
