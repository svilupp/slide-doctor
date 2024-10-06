import yaml
import os

# Get the path to the config file
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
config_path="config/config.yaml"

def load_config(config_path):
    # Read the YAML file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config(config_path)

# Iterate through each checker in the config
for checker in config['checkers']:
    print(f"Checker: {checker['name']}")
    print(f"Task: {checker['task']}")
    print(f"Type: {checker['type']}")
    print(f"Criteria: {checker['criteria']}")
    print("\n")

