from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.middleware import register_middleware


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "https://eva-ai.vercel.app",
                    "http://localhost:3000",
                    "http://localhost:5500",
                    "http://127.0.0.1:5500",
                    "http://localhost:8000",
                ]
            }
        },
        supports_credentials=True,
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
