import re
import json


def sanitize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\0", "")
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()


def truncate_text(text, max_length=4096):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def parse_json_safe(text):
    if not text:
        return None
    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, AttributeError):
        return None


def success_response(data=None, message=None, status=200):
    resp = {"success": True}
    if data is not None:
        resp["data"] = data
    if message:
        resp["message"] = message
    return resp, status


def error_response(error="Something went wrong", status=500):
    return {"success": False, "error": error}, status
