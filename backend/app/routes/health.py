import logging
import time

from flask import Blueprint, jsonify

from app.services.ai import key_manager
from app.config import Config

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)

start_time = time.time()


@health_bp.route("/")
@health_bp.route("/health")
def health():
    uptime = time.time() - start_time

    return jsonify(
        {
            "status": "ok",
            "service": "Eva AI Backend",
            "model": Config.GROQ_MODEL,
            "uptime_seconds": round(uptime, 2),
            "api_keys": key_manager.stats,
        }
    )
