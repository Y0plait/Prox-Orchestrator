import asyncio
import tomlkit
import logging
import json
from aiohttp import ClientSession
from pathlib import Path
from .constants import DEFAULT_CONFIG_FILE_PATH, DEFAULT_ANSWER_FILE_PATH, DYNAMIC_INVENTORY_FILE, NODES_DATA_STORAGE_PATH
from .inventory import update_dynamic_inventory

def assert_default_answer_file_exists():
    if not DEFAULT_ANSWER_FILE_PATH.exists():
        raise FileNotFoundError(f"Missing {DEFAULT_ANSWER_FILE_PATH}")

def assert_default_answer_file_parseable():
    with open(DEFAULT_ANSWER_FILE_PATH) as f:
        try:
            tomlkit.parse(f.read())
        except Exception as e:
            raise RuntimeError(f"Error parsing default answer file: {e}")

def ensure_dynamic_inventory_file_exists():
    if not DYNAMIC_INVENTORY_FILE.exists():
        DYNAMIC_INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DYNAMIC_INVENTORY_FILE, "w") as f:
            json.dump({}, f, indent=2)

def create_file_answer(request_data: dict, ip_remote: str) -> str:
    with open(DEFAULT_ANSWER_FILE_PATH) as file:
        answer = tomlkit.parse(file.read())

    with open(DEFAULT_CONFIG_FILE_PATH) as file:
        config = tomlkit.parse(file.read())

    uuid = request_data.get("dmi", {}).get("system", {}).get("uuid", "unknown")
    uuid_id = uuid[-4:]

    fqdn = config["machine_template_name"] + uuid_id + config["machine_net_dn"]
    answer["global"]["fqdn"] = fqdn
    answer["network"]["cidr"] = ip_remote + config["machine_net_mask"]
    answer["network"]["dns"] = config["machine_net_dns"]
    answer["network"]["gateway"] = config["machine_net_gateway"]
    answer["network"]["filter"] = {"ID_VENDOR_FROM_DATABASE": config["machine_net_int"]}

    node_dir = NODES_DATA_STORAGE_PATH.joinpath(fqdn)
    node_dir.mkdir(parents=True, exist_ok=True)

    with open(node_dir.joinpath("config.toml"), "w") as f:
        f.write(tomlkit.dumps(answer))

    update_dynamic_inventory(fqdn, "installing")

    return tomlkit.dumps(answer)

async def create_webhook_answer(webhooks: dict) -> str:
    results = {}

    async with ClientSession() as session:
        for url, details in webhooks.items():
            try:
                payload = details.get("payload", {})
                async with session.post(url, json=payload) as resp:
                    results[url] = {
                        "status": resp.status,
                        "response": await resp.text(),
                    }
            except Exception as e:
                results[url] = {"status": "error", "error": str(e)}
                logging.exception(f"Webhook POST failed: {url}")
    
    return json.dumps(results, indent=2)
