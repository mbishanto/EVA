import logging

from flask import Blueprint, jsonify, request, g

from app.middleware import require_auth
from app.utils.validators import validate_conversation_id
from app.services.database import db

logger = logging.getLogger(__name__)

conversations_bp = Blueprint("conversations", __name__)


@conversations_bp.route("/conversations", methods=["GET"])
@require_auth
def list_conversations():
    try:
        user_id = g.user_id
        search_query = request.args.get("q", "").strip()

        if search_query:
            conversations = db.search_conversations(user_id, search_query)
        else:
            conversations = db.get_conversations(user_id)

        return jsonify({"success": True, "data": conversations})

    except Exception as e:
        logger.error("Error listing conversations: %s", e)
        return jsonify({"success": False, "error": "Failed to list conversations"}), 500


@conversations_bp.route("/conversations", methods=["POST"])
@require_auth
def create_conversation():
    try:
        user_id = g.user_id
        data = request.get_json(silent=True) or {}
        title = data.get("title", "New Chat")

        conversation = db.create_conversation(user_id, title)
        return jsonify({"success": True, "data": conversation}), 201

    except Exception as e:
        logger.error("Error creating conversation: %s", e)
        return jsonify({"success": False, "error": "Failed to create conversation"}), 500


@conversations_bp.route("/conversations/<conversation_id>", methods=["GET"])
@require_auth
@validate_conversation_id
def get_conversation(conversation_id):
    try:
        user_id = g.user_id
        conversation = db.get_conversation(conversation_id, user_id)

        if not conversation:
            return jsonify({"success": False, "error": "Conversation not found"}), 404

        messages = db.get_messages(conversation_id)

        return jsonify(
            {
                "success": True,
                "data": {
                    "conversation": conversation,
                    "messages": messages,
                },
            }
        )

    except Exception as e:
        logger.error("Error getting conversation: %s", e)
        return jsonify({"success": False, "error": "Failed to get conversation"}), 500


@conversations_bp.route("/conversations/<conversation_id>/rename", methods=["PATCH"])
@require_auth
@validate_conversation_id
def rename_conversation(conversation_id):
    try:
        user_id = g.user_id
        data = request.get_json(silent=True)
        title = data.get("title", "").strip()

        if not title or len(title) > 200:
            return jsonify({"success": False, "error": "Title is required (max 200 chars)"}), 400

        conversation = db.get_conversation(conversation_id, user_id)
        if not conversation:
            return jsonify({"success": False, "error": "Conversation not found"}), 404

        db.update_conversation_title(conversation_id, user_id, title)

        return jsonify({"success": True, "data": {"title": title}})

    except Exception as e:
        logger.error("Error renaming conversation: %s", e)
        return jsonify({"success": False, "error": "Failed to rename conversation"}), 500


@conversations_bp.route("/conversations/<conversation_id>", methods=["DELETE"])
@require_auth
@validate_conversation_id
def delete_conversation(conversation_id):
    try:
        user_id = g.user_id

        conversation = db.get_conversation(conversation_id, user_id)
        if not conversation:
            return jsonify({"success": False, "error": "Conversation not found"}), 404

        db.delete_conversation(conversation_id, user_id)

        return jsonify({"success": True, "message": "Conversation deleted"})

    except Exception as e:
        logger.error("Error deleting conversation: %s", e)
        return jsonify({"success": False, "error": "Failed to delete conversation"}), 500


@conversations_bp.route("/conversations/<conversation_id>/export", methods=["GET"])
@require_auth
@validate_conversation_id
def export_conversation(conversation_id):
    try:
        user_id = g.user_id

        conversation = db.get_conversation(conversation_id, user_id)
        if not conversation:
            return jsonify({"success": False, "error": "Conversation not found"}), 404

        messages = db.get_messages(conversation_id)

        export_data = {
            "title": conversation["title"],
            "exported_at": __import__("datetime").datetime.now().isoformat(),
            "messages": [
                {"role": m["role"], "content": m["content"]} for m in messages
            ],
        }

        return jsonify({"success": True, "data": export_data})

    except Exception as e:
        logger.error("Error exporting conversation: %s", e)
        return jsonify({"success": False, "error": "Failed to export conversation"}), 500
