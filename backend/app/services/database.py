import logging
import uuid
from datetime import datetime, timezone

from supabase import create_client

from app.config import Config

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self):
        self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    # ==================== Users ====================

    def get_user(self, user_id):
        response = (
            self.client.table("users")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data:
            return response.data[0]
        return {
            "user_id": user_id,
            "name": "",
            "notes": [],
            "summary": "",
            "emotions": [],
            "relationship": {
                "favorite_topics": [],
                "friendship_level": 0,
            },
        }

    def save_user(self, user_id, profile):
        self.client.table("users").upsert(
            {
                "user_id": user_id,
                "name": profile.get("name", ""),
                "notes": profile.get("notes", []),
                "summary": profile.get("summary", ""),
                "emotions": profile.get("emotions", []),
                "relationship": profile.get(
                    "relationship",
                    {"favorite_topics": [], "friendship_level": 0},
                ),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

    # ==================== Conversations ====================

    def create_conversation(self, user_id, title=None):
        conv_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "id": conv_id,
            "user_id": user_id,
            "title": title or "New Chat",
            "created_at": now,
            "updated_at": now,
        }
        self.client.table("conversations").insert(data).execute()
        return data

    def get_conversations(self, user_id):
        response = (
            self.client.table("conversations")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return response.data or []

    def get_conversation(self, conversation_id, user_id):
        response = (
            self.client.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def update_conversation_title(self, conversation_id, user_id, title):
        now = datetime.now(timezone.utc).isoformat()
        self.client.table("conversations").update(
            {"title": title, "updated_at": now}
        ).eq("id", conversation_id).eq("user_id", user_id).execute()

    def delete_conversation(self, conversation_id, user_id):
        self.client.table("messages").delete().eq(
            "conversation_id", conversation_id
        ).execute()
        self.client.table("conversations").delete().eq(
            "id", conversation_id
        ).eq("user_id", user_id).execute()

    def generate_title(self, conversation_id, user_id, message):
        response = (
            self.client.table("conversations")
            .update({"title": message[:60] + ("..." if len(message) > 60 else "")})
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )

    # ==================== Messages ====================

    def save_message(self, conversation_id, role, content, token_count=0):
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "token_count": token_count,
            "created_at": now,
        }
        self.client.table("messages").insert(data).execute()

        self.client.table("conversations").update(
            {"updated_at": now}
        ).eq("id", conversation_id).execute()

        return data

    def get_messages(self, conversation_id):
        response = (
            self.client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", asc=True)
            .execute()
        )
        return response.data or []

    def search_conversations(self, user_id, query):
        response = (
            self.client.table("conversations")
            .select("*")
            .eq("user_id", user_id)
            .ilike("title", f"%{query}%")
            .order("updated_at", desc=True)
            .execute()
        )
        return response.data or []


db = DatabaseService()
