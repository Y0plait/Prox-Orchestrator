import tomlkit
from .constants import DEFAULT_CONFIG_FILE_PATH, DEFAULT_ANSWER_FILE_PATH

def load_config():
    with open(DEFAULT_CONFIG_FILE_PATH) as file:
        return tomlkit.parse(file.read())

def load_default_answer():
    with open(DEFAULT_ANSWER_FILE_PATH) as file:
        return tomlkit.parse(file.read())
