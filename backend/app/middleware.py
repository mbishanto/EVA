import time
import logging
from functools import wraps

import jwt
from flask import request, jsonify, g

from app.config import Config

logger = logging.getLogger(__name__)

_rate_limit_store = {}


def verify_jwt(token):
    try:
        payload = jwt.decode(
            token,
            Config.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        payload = verify_jwt(token)

        if payload is None:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.user_id = payload.get("sub")
        g.token_payload = payload

        return f(*args, **kwargs)

    return decorated


def optional_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = verify_jwt(token)
            if payload:
                g.user_id = payload.get("sub")
                g.token_payload = payload
            else:
                g.user_id = None
        else:
            g.user_id = None

        return f(*args, **kwargs)

    return decorated


def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        now = time.time()
        window = Config.RATE_LIMIT_WINDOW
        limit = Config.RATE_LIMIT

        if ip not in _rate_limit_store:
            _rate_limit_store[ip] = []

        _rate_limit_store[ip] = [
            t for t in _rate_limit_store[ip] if now - t < window
        ]

        if len(_rate_limit_store[ip]) >= limit:
            logger.warning("Rate limit exceeded for IP: %s", ip)
            return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

        _rate_limit_store[ip].append(now)

        return f(*args, **kwargs)

    return decorated


def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-XSS-Protection"] = "1; mode=block"
    resp.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
        "style-src 'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://*.supabase.co https://api.groq.com; "
        "frame-ancestors 'none'"
    )
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["Cache-Control"] = "no-store, max-age=0"
    resp.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    return resp


def register_middleware(app):
    app.after_request(security_headers)
