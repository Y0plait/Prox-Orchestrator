from aiohttp import web
from .webhook_handler import webhook
from .answer_handler import answer

def setup_routes(app: web.Application):
    app.router.add_post("/webhook/", webhook)
    app.router.add_post("/answer/", answer)
