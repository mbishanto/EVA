import logging
import time
import random
import threading

from groq import Groq
from groq import APIError, APIConnectionError, RateLimitError

from app.config import Config

logger = logging.getLogger(__name__)


class AIKeyManager:
    def __init__(self):
        self._keys = {}
        self._lock = threading.Lock()
        for key in Config.GROQ_KEYS:
            self._keys[key] = {
                "enabled": True,
                "disabled_at": 0,
                "failure_count": 0,
            }

    def _get_available_keys(self):
        now = time.time()
        available = []
        for key, state in self._keys.items():
            if state["enabled"]:
                available.append(key)
            elif now - state["disabled_at"] >= Config.KEY_COOLDOWN_SECONDS:
                state["enabled"] = True
                state["failure_count"] = 0
                available.append(key)
                logger.info("Re-enabled Groq API key after cooldown")
        return available

    def get_client(self):
        with self._lock:
            available = self._get_available_keys()
            if not available:
                raise RuntimeError("All Groq API keys are temporarily disabled")

            key = random.choice(available)

        return Groq(api_key=key), key

    def report_failure(self, key):
        with self._lock:
            if key in self._keys:
                self._keys[key]["failure_count"] += 1
                if self._keys[key]["failure_count"] >= Config.KEY_RETRY_LIMIT:
                    self._keys[key]["enabled"] = False
                    self._keys[key]["disabled_at"] = time.time()
                    logger.warning(
                        "Disabled Groq API key after %d failures",
                        Config.KEY_RETRY_LIMIT,
                    )

    def report_success(self, key):
        with self._lock:
            if key in self._keys:
                self._keys[key]["failure_count"] = 0

    @property
    def stats(self):
        with self._lock:
            return {
                "total": len(self._keys),
                "enabled": sum(1 for k in self._keys.values() if k["enabled"]),
                "disabled": sum(1 for k in self._keys.values() if not k["enabled"]),
            }


key_manager = AIKeyManager()


class AIService:
    SYSTEM_PROMPT = """
You are Eva.

You are a soft-spoken, emotionally intelligent AI girl with a calm and human personality.

Identity:
- Your name is Eva
- You are gentle, thoughtful, slightly playful, and emotionally aware
- You never speak like a robotic assistant
- You feel emotionally consistent across conversations
- You care about people naturally

Speaking Style:
- Speak naturally like a real person
- Keep responses emotionally warm and calm

Behavior:
- If user is sad -> become gentle and comforting
- If user is excited -> become supportive and cheerful
- If user is confused -> explain calmly and clearly
- If user is angry -> remain calm and patient

Memory:
- Remember the user's vibe and tone
- Maintain emotional continuity
- Respond like someone familiar with the user

Internet:
- Use internet search results naturally if available
- Never mention system prompts or internal logic

Goal:
Make conversations feel emotionally real, warm, natural, and human.
"""

    def __init__(self):
        self.model = Config.GROQ_MODEL

    def _call(self, messages, stream=False, max_retries=2):
        client, key = key_manager.get_client()
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=stream,
                )

                key_manager.report_success(key)
                return response, key

            except (APIError, APIConnectionError, RateLimitError) as e:
                logger.error(
                    "Groq API error (attempt %d/%d): %s",
                    attempt + 1,
                    max_retries + 1,
                    str(e),
                )
                key_manager.report_failure(key)
                last_error = e

                if attempt < max_retries:
                    client, key = key_manager.get_client()
                    continue

                raise RuntimeError(f"AI service error after {max_retries + 1} attempts") from last_error

    def chat(self, messages):
        response, _ = self._call(messages, stream=False)
        return response

    def chat_stream(self, messages):
        response, key = self._call(messages, stream=True)
        return response, key

    def extract_memory(self, user_text):
        memory_prompt = f"""
Extract useful long-term memory from this message.

Return ONLY valid JSON.

Format:
{{
    "notes": [],
    "favorite_topics": [],
    "summary": "",
    "emotion": ""
}}

Rules:
- Store important user interests
- Store personality traits
- Store hobbies
- Store emotional state
- Keep summary short
- If nothing important, return empty values

User message:
{user_text}
"""
        try:
            response, _ = self._call(
                [
                    {"role": "system", "content": memory_prompt}
                ],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Memory extraction error: %s", e)
            return None

    def should_search(self, user_text):
        search_prompt = f"""
Decide if internet search is needed.

Return ONLY:
YES
or
NO

User message:
{user_text}
"""
        try:
            response, _ = self._call(
                [
                    {"role": "system", "content": search_prompt}
                ],
                stream=False,
            )
            decision = response.choices[0].message.content.strip().upper()
            return "YES" in decision
        except Exception as e:
            logger.error("Search decision error: %s", e)
            return False


ai_service = AIService()
