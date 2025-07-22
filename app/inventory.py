import json
from .constants import DYNAMIC_INVENTORY_FILE

try:
    with open(DYNAMIC_INVENTORY_FILE) as f:
        DYNAMIC_INVENTORY = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    DYNAMIC_INVENTORY = {}

def update_dynamic_inventory(fqdn: str, status: str):
    DYNAMIC_INVENTORY[fqdn] = status
    with open(DYNAMIC_INVENTORY_FILE, "w") as f:
        json.dump(DYNAMIC_INVENTORY, f, indent=2)

def all_nodes_installed() -> bool:
    return all(status == "installed" for status in DYNAMIC_INVENTORY.values())
