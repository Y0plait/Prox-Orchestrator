import time
import json
import logging
from aiohttp import web
from .utils import create_webhook_answer
from .ansible_runner import run_ansible_playbook
from .inventory import update_dynamic_inventory, all_nodes_installed, DYNAMIC_INVENTORY, DYNAMIC_INVENTORY_FILE

LAST_UPDATE_TIMESTAMP = time.time()
ANSIBLE_LAUNCHED = False

async def webhook(request: web.Request):
    global LAST_UPDATE_TIMESTAMP, ANSIBLE_LAUNCHED

    try:
        request_data = json.loads(await request.text())
    except json.JSONDecodeError as e:
        return web.Response(status=500, text=f"JSON parse error: {e}")

    logging.info(f"Incoming webhook from {request.remote}: {request_data}")

    try:
        fqdn = request_data["fqdn"]
        webhooks = { 
            "https://discord.com/api/webhooks/1394722461928521911/dsVlXOeS_WakkcdNUqHNVBUJRdnLP5_NR5CZi-xhVJB1ewrJ1dubjqnHqxmkSyvN5a11": {
                "payload": {
                    "name": "Proxmox Test",
                    "type": 1,
                    "channel_id": "1394722424901206220",
                    "token": "dsVlXOeS_WakkcdNUqHNVBUJRdnLP5_NR5CZi-xhVJB1ewrJ1dubjqnHqxmkSyvN5a11",
                    "avatar": "null",
                    "guild_id": "1394722424380985414",
                    "id": "1394722461928521911",
                    "application_id": "null",
                    "user": {
                        "username": "test",
                        "discriminator": "7479",
                        "id": "190320984123768832",
                        "avatar": "b004ec1740a63ca06ae2e14c5cee11f3",
                        "public_flags": 131328
                    },
                    "username": "ProxmoXer",
                    "avatar_url": "https://img.icons8.com/color/600/proxmox.png",
                    "content": "Good news !",
                    "embeds": [
                        {
                        "author": {
                            "name": "Prox-Orchestrator",
                            "url": "https://github.com/Y0plait/Prox-Orchestrator",
                            "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png"
                        },
                        "title": "Successful Install !",
                        "description": f"Proxmox has been **successfuly** deployed on **{request_data["fqdn"]}**!",
                        "color": 15258703,
                        "fields": [
                            {
                            "name": "Management IP",
                            "value": f"{request.remote}",
                            "inline": "true"
                            },
                            {
                            "name": "System Filesystem",
                            "value": f"{request_data["filesystem"]}",
                            "inline": "true"
                            },
                            {
                            "name": "WebUI Acceess",
                            "value": f"[Here](https://{request.remote}:8006)"
                            },
                            {
                            "name": "CPU Model",
                            "value": f"{request_data["cpu-info"]["model"]}",
                            "inline": "true"
                            }
                        ]
                        }
                    ]
                }
            }
         }  # Put your Discord webhook logic here as before

        answer = await create_webhook_answer(webhooks)
        logging.info(f"Webhook dispatched: {answer}")

        update_dynamic_inventory(fqdn, "installed")
        LAST_UPDATE_TIMESTAMP = time.time()

        if not ANSIBLE_LAUNCHED and all_nodes_installed():
            logging.info("All nodes installed. Launching Ansible.")
            ANSIBLE_LAUNCHED = True
            request.app["ansible_task"] = request.loop.create_task(run_ansible_playbook())

        return web.Response(text=answer)
    except Exception as e:
        logging.exception("Webhook handler failed")
        return web.Response(status=500, text=str(e))
