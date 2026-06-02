import json
import os
from typing import Any

def save_output(filename: str, data: Any):
    """Saves data to the outputs directory."""
    os.makedirs("outputs", exist_ok=True)
    filepath = os.path.join("outputs", filename)
    
    if isinstance(data, (dict, list)):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(data))
    
    print(f"Saved output to {filepath}")

def load_prompt(filename: str) -> str:
    """Loads a prompt from the prompts directory."""
    filepath = os.path.join("prompts", filename)
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
