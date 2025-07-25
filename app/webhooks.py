import json
import logging
from aiohttp import web, ClientSession

class WebhookFormer():
    async def __init__(self, request: web.Request):
        self.request = request

        # Load the initial request (Proxmox end install process)
        try:
            self.request_data = json.loads(await self.request.text())
        except json.JSONDecodeError as e:
            return web.Response(status=500, text=f"JSON parse error: {e}")

    async def __getUrl(self, url: str):
        result = {}

        try:
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    result[url] = {
                        "status": resp.status,
                        "response": await resp.text(),
                    }
        except Exception as e:
            result[url] = {"status": "error", "error": str(e)}
            logging.exception(f"GET request to url failed: {url}")

        return result

    async def discord(self, url: str) -> dict:
        """
        Forms a webhook request for Discord
        """
        # GET request to webhook url to get channel_id, id...
        webhookDetails = json.loads(self.__getUrl(url))

        discordWebhookPayload = {
                "payload": {
                    "name": "Proxmox Test",
                    "type": 1,
                    "channel_id": f"{webhookDetails['channel_id']}",
                    "token": f"{webhookDetails['token']}",
                    "avatar": f"{webhookDetails['avatar']}",
                    "guild_id": f"{webhookDetails['guild_id']}",
                    "id": f"{webhookDetails['id']}",
                    "application_id": f"{webhookDetails['application_id']}",
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
                        "description": f"Proxmox has been **successfuly** deployed on **{self.request_data["fqdn"]}**!",
                        "color": 15258703,
                        "fields": [
                            {
                            "name": "Management IP",
                            "value": f"{self.request.remote}",
                            "inline": "true"
                            },
                            {
                            "name": "System Filesystem",
                            "value": f"{self.request_data["filesystem"]}",
                            "inline": "true"
                            },
                            {
                            "name": "WebUI Acceess",
                            "value": f"[Here](https://{self.request.remote}:8006)"
                            },
                            {
                            "name": "CPU Model",
                            "value": f"{self.request_data["cpu-info"]["model"]}",
                            "inline": "true"
                            }
                        ]
                        }
                    ]
                }
            }

        return discordWebhookPayload
