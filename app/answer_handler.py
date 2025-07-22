import json
import logging
from aiohttp import web
from .utils import create_file_answer

async def answer(request: web.Request):
    try:
        request_data = json.loads(await request.text())
    except json.JSONDecodeError as e:
        return web.Response(status=500, text=f"JSON parse error: {e}")

    logging.info(f"Answer request from {request.remote}: {request_data}")

    try:
        response = create_file_answer(request_data, request.remote)
        return web.Response(text=response)
    except Exception as e:
        logging.exception("Answer handler failed")
        return web.Response(status=500, text=str(e))
