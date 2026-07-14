from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.middleware import register_middleware


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ------------------------------------------------------------------
    # CORS configuration
    # ------------------------------------------------------------------
    # Origins are loaded from the FRONTEND_URL environment variable.
    # See app/config.py for details on how the list is built.
    # ------------------------------------------------------------------
    # To add a new frontend domain:
    #   Append it to the FRONTEND_URL env var, e.g.:
    #     FRONTEND_URL=https://eva-me.vercel.app,https://eva-ai.vercel.app
    #   No code changes are required.
    # ------------------------------------------------------------------
    CORS(
        app,
        resources={
            r"/*": {
                "origins": config_class.FRONTEND_URLS,
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
                "supports_credentials": False,
            }
        },
    )

    register_middleware(app)

    from app.routes.health import health_bp
    from app.routes.chat import chat_bp
    from app.routes.conversations import conversations_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(auth_bp)

    return app
