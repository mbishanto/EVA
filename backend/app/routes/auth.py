import logging

from flask import Blueprint, jsonify, request

from app.middleware import require_auth
from app.utils.validators import validate_auth_request

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/me", methods=["GET"])
@require_auth
def me():
    from flask import g
    return jsonify(
        {
            "success": True,
            "data": {
                "user_id": g.user_id,
            },
        }
    )
