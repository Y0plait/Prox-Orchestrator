from pathlib import Path

DEFAULT_CONFIG_DIR_PATH = Path("config/")
DEFAULT_CONFIG_FILE_PATH = DEFAULT_CONFIG_DIR_PATH.joinpath("config.toml")
DEFAULT_ANSWER_FILE_PATH = DEFAULT_CONFIG_DIR_PATH.joinpath("default.toml")
NODES_DATA_STORAGE_PATH = Path("nodes/")
DYNAMIC_INVENTORY_FILE = NODES_DATA_STORAGE_PATH.joinpath("dynamic-inventory.json")
