import yaml
import re

def load_config(config_path: str):
    # Read the YAML file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def extract_slide_number(path: str) -> int:
    """
    Extracts the last three digits from the given path and returns them as an integer.
    Uses regex and removes the file extension first.
    
    Args:
    path (str): The file path to extract the number from.
    
    Returns:
    int: The extracted three-digit number.
    """
    # Remove the file extension
    path_without_extension = path.rsplit('.', 1)[0]
    
    # Use regex to find the last three digits
    match = re.search(r'(\d{3})$', path_without_extension)
    
    if match:
        return int(match.group(1))
    else:
        raise ValueError("No three-digit number found at the end of the path")

# Example usage:
# path = 'data/03-dickinson-basic002.png'
# slide_number = extract_slide_number(path)