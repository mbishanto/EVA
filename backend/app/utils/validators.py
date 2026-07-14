import re

from flask import request, jsonify
from functools import wraps


def validate_chat_request(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        message = data.get("message")
        if not message or not isinstance(message, str):
            return jsonify({"error": "Field 'message' is required and must be a string"}), 400

        message = message.strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        if len(message) > 4096:
            return jsonify({"error": "Message exceeds maximum length of 4096 characters"}), 400

        return f(*args, **kwargs)

    return decorated


def validate_auth_request(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not isinstance(email, str):
            return jsonify({"error": "Email is required"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        if not password or not isinstance(password, str) or len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        return f(*args, **kwargs)

    return decorated


def validate_conversation_id(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        conv_id = kwargs.get("conversation_id")
        if not conv_id or not isinstance(conv_id, str) or len(conv_id) > 64:
            return jsonify({"error": "Invalid conversation ID"}), 400
        return f(*args, **kwargs)

    return decorated
