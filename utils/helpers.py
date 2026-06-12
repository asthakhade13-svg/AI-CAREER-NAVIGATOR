import json
from typing import Union


def save_json(data: Union[dict, list], file_path: str) -> None:
    """Saves a dictionary or list to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_json(file_path: str) -> Union[dict, list]:
    """Loads a dictionary or list from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
