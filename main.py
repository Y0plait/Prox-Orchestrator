import logging
from aiohttp import web
from app.routes import setup_routes
from app.utils import (
    assert_default_answer_file_exists,
    assert_default_answer_file_parseable,
    ensure_dynamic_inventory_file_exists,
)

def main():
    # Pre-run checks
    assert_default_answer_file_exists()
    assert_default_answer_file_parseable()
    ensure_dynamic_inventory_file_exists()

    logging.basicConfig(level=logging.INFO)

    # Setup web app
    app = web.Application()
    setup_routes(app)

    web.run_app(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
