"""Flask application factory."""

import threading

from flask import Flask

from .routes    import bp
from .worker    import refresh_loop
from .dashboard import DASHBOARD


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(bp)

    @app.route("/")
    def index():
        return DASHBOARD

    threading.Thread(target=refresh_loop, daemon=True).start()
    return app
