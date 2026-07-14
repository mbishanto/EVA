import logging
import json

from flask import Blueprint, jsonify, request, g, Response, stream_with_context

from app.middleware import require_auth, rate_limit
from app.utils.validators import validate_chat_request
from app.services.ai import ai_service, key_manager
from app.services.database import db
from app.services.memory import memory_service
from app.services.search import search_service

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)


def _prepare_chat(user_text, conversation_id, user_id):
    mood = memory_service.detect_mood(user_text)
    time_context = memory_service.get_time_context()

    if not conversation_id:
        conversation = db.create_conversation(user_id, user_text[:60])
        conversation_id = conversation["id"]
        is_new = True
    else:
        conversation = db.get_conversation(conversation_id, user_id)
        if not conversation:
            return None, ("error_response", {"error": "Conversation not found"}, 404)
        is_new = False

    profile = db.get_user(user_id)

    if "relationship" not in profile:
        profile["relationship"] = {
            "favorite_topics": [],
            "friendship_level": 0,
        }

    name = memory_service.extract_name(user_text)
    if name:
        profile["name"] = name

    profile["relationship"]["friendship_level"] += 1

    memory_text = ai_service.extract_memory(user_text)
    if memory_text:
        profile = memory_service.merge_memory_data(profile, memory_text)

    web_results = ""
    if ai_service.should_search(user_text):
        web_results = search_service.web_search(user_text)

    history = db.get_messages(conversation_id)

    messages = [
        {"role": "system", "content": ai_service.SYSTEM_PROMPT},
        {"role": "system", "content": f"time: {time_context}"},
        {
            "role": "system",
            "content": f"""
User name:
{profile.get('name', '')}

User summary:
{profile.get('summary', '')}

User emotions:
{profile.get('emotions', [])}

User notes:
{profile.get('notes', [])}

Relationship:
{profile.get('relationship', {})}

Internet results:
{web_results}

Mood:
{mood}
""",
        },
    ]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_text})

    return {
        "conversation_id": conversation_id,
        "profile": profile,
        "history": history,
        "mood": mood,
        "messages": messages,
        "is_new": is_new,
    }, None


def _save_conversation(conversation_id, user_id, profile, user_text, reply, token_count, is_new):
    db.save_message(conversation_id, "user", user_text)
    db.save_message(conversation_id, "assistant", reply, token_count)
    db.save_user(user_id, profile)
    if is_new:
        db.generate_title(conversation_id, user_id, user_text)


@chat_bp.route("/chat", methods=["POST"])
@require_auth
@rate_limit
@validate_chat_request
def chat():
    try:
        data = request.get_json(silent=True)
        user_text = data["message"].strip()
        conversation_id = data.get("conversation_id")
        use_stream = data.get("stream", False)
        user_id = g.user_id

        prep_result, error = _prepare_chat(user_text, conversation_id, user_id)
        if error:
            return jsonify(error[1]), error[2]

        conversation_id = prep_result["conversation_id"]
        profile = prep_result["profile"]
        history = prep_result["history"]
        mood = prep_result["mood"]
        messages = prep_result["messages"]
        is_new = prep_result["is_new"]

        if use_stream:
            return _stream_response(messages, conversation_id, user_id, profile, user_text, mood)

        response = ai_service.chat(messages)
        reply = response.choices[0].message.content
        usage = response.usage
        token_count = usage.total_tokens if usage else 0

        _save_conversation(conversation_id, user_id, profile, user_text, reply, token_count, is_new)

        return jsonify(
            {
                "success": True,
                "data": {
                    "reply": reply,
                    "conversation_id": conversation_id,
                    "tokens": {
                        "total": token_count,
                        "prompt": usage.prompt_tokens if usage else 0,
                        "completion": usage.completion_tokens if usage else 0,
                    },
                    "mood": mood,
                },
            }
        )

    except RuntimeError as e:
        logger.error("Chat error: %s", e)
        return jsonify({"success": False, "error": "AI service temporarily unavailable"}), 503
    except Exception as e:
        logger.error("Unexpected chat error: %s", e, exc_info=True)
        return jsonify({"success": False, "error": "Internal server error"}), 500


def _stream_response(messages, conversation_id, user_id, profile, user_text, mood):
    def generate():
        full_reply = ""
        stream, key = ai_service.chat_stream(messages)

        try:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_reply += content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"

            usage = None
            if hasattr(chunk, 'usage') and chunk.usage:
                usage = chunk.usage

            token_count = usage.total_tokens if usage else 0
            _save_conversation(conversation_id, user_id, profile, user_text, full_reply, token_count, False)

            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id, 'tokens': {'total': token_count}})}\n\n"

        except Exception as e:
            logger.error("Streaming error: %s", e)
            yield f"data: {json.dumps({'type': 'error', 'error': 'Stream interrupted'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
