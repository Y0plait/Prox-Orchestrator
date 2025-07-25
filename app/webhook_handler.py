import time
import json
import logging
from aiohttp import web
from .utils import create_webhook_answer
from .ansible_runner import run_ansible_playbook
from .inventory import update_dynamic_inventory, all_nodes_installed
from .constants import WEBHOOKS_URL_FILE
from .webhooks import WebhookFormer

LAST_UPDATE_TIMESTAMP = time.time()
ANSIBLE_LAUNCHED = False

async def webhook(request: web.Request):
    global LAST_UPDATE_TIMESTAMP, ANSIBLE_LAUNCHED

    try:
        generator = WebhookFormer(request)
        
        discordWebhookUrl = "*********"
        webhooks = {
            discordWebhookUrl: generator.discord(discordWebhookUrl)
        }

        fqdn = generator.request_data

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
