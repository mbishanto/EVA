from flask import Flask, request, jsonify
from flask_cors import CORS

from groq import Groq
from supabase import create_client
from duckduckgo_search import DDGS

import random
import os
import json
import re

from datetime import datetime

# ================== APP ==================

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# ================== ENV ==================

keys = os.getenv("GROQ_KEYS", "")
GROQ_KEYS = keys.split(",") if keys else []

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not GROQ_KEYS:
    raise ValueError("Missing GROQ_KEYS")

# ================== MEMORY ==================

user_memory = {}
MAX_HISTORY = 1000

# ================== SUPABASE ==================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ================== AI CLIENT ==================

def get_client():

    return Groq(
        api_key=random.choice(GROQ_KEYS)
    )

# ================== USER ==================

def get_user(user_id):

    response = supabase.table("users") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    data = response.data

    if data:
        return data[0]

    return {
        "name": "",
        "notes": [],
        "summary": "",
        "emotions": [],
        "relationship": {
            "favorite_topics": [],
            "friendship_level": 0
        }
    }

def save_user(user_id, profile):

    supabase.table("users").upsert({
        "user_id": user_id,
        "name": profile.get("name", ""),
        "notes": profile.get("notes", []),
        "summary": profile.get("summary", ""),
        "emotions": profile.get("emotions", []),
        "relationship": profile.get("relationship", {
            "favorite_topics": [],
            "friendship_level": 0
        })
    }).execute()

# ================== WEB SEARCH ==================

def web_search(query):

    results_text = ""

    try:

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=5
                )
            )

        for r in results:

            title = r.get("title", "")
            body = r.get("body", "")

            results_text += f"""
Title: {title}

Snippet: {body}

"""

    except Exception as e:

        results_text = f"Search failed: {str(e)}"

    return results_text

# ================== TIME ==================

def get_time_context():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "morning"

    elif 12 <= hour < 18:
        return "afternoon"

    elif 18 <= hour < 24:
        return "evening"

    return "night"

# ================== PERSONALITY ==================

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
- If user is sad → become gentle and comforting
- If user is excited → become supportive and cheerful
- If user is confused → explain calmly and clearly
- If user is angry → remain calm and patient

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

# ================== MOOD ==================

def detect_mood(text):

    text = text.lower()

    if any(w in text for w in [
        "sad",
        "depressed",
        "tired"
    ]):
        return "sad"

    if any(w in text for w in [
        "error",
        "problem",
        "issue"
    ]):
        return "frustrated"

    return "normal"

# ================== HOME ==================

@app.route("/")
def home():
    return "Eva Backend Running"

# ================== CHAT ==================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        user_id = data.get("user_id", "guest")

        user_text = data["message"]

        mood = detect_mood(user_text)

        if user_id not in user_memory:
            user_memory[user_id] = []

        user_memory[user_id].append({
            "role": "user",
            "content": user_text
        })

        user_memory[user_id] = user_memory[user_id][-MAX_HISTORY:]

        profile = get_user(user_id)

        if "relationship" not in profile:

            profile["relationship"] = {
                "favorite_topics": [],
                "friendship_level": 0
            }

        client = get_client()

        # ================== NAME SAVE ==================

        name_match = re.search(
            r"(my name is|i am|i'm)\s+([A-Za-z ]+)",
            user_text,
            re.IGNORECASE
        )

        if name_match:

            detected_name = name_match.group(2).strip()

            profile["name"] = detected_name

        # ================== MEMORY UPDATE ==================

        profile["relationship"]["friendship_level"] += 1

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

            memory_response = client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[
                    {
                        "role": "system",
                        "content": memory_prompt
                    }
                ]

            )

            memory_text = (
                memory_response
                .choices[0]
                .message
                .content
            )

            memory_text = re.sub(
                r"```json|```",
                "",
                memory_text
            ).strip()

            memory_data = json.loads(memory_text)

            # notes

            for note in memory_data.get("notes", []):

                if note not in profile["notes"]:

                    profile["notes"].append(note)

            # favorite topics

            for topic in memory_data.get("favorite_topics", []):

                if topic not in profile["relationship"]["favorite_topics"]:

                    profile["relationship"]["favorite_topics"].append(topic)

            # summary

            if memory_data.get("summary"):

                profile["summary"] = memory_data["summary"]

            # emotions

            emotion = memory_data.get("emotion")

            if emotion:

                if emotion not in profile["emotions"]:

                    profile["emotions"].append(emotion)

        except Exception as e:

            print("MEMORY ERROR:", e)

        # ================== SEARCH ==================

        web_results = ""

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

            search_decision = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": search_prompt
                    }
                ]
            )

            decision = (
                search_decision
                .choices[0]
                .message
                .content
                .strip()
                .upper()
            )

            if "YES" in decision:

                web_results = web_search(
                    user_text
                )

        except:
            pass

        # ================== TIME ==================

        time_context = get_time_context()

        # ================== PROMPT ==================

        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "system",
                "content": f"time: {time_context}"
            },

            {
                "role": "system",
                "content": f"""
User name:
{profile['name']}

User summary:
{profile['summary']}

User emotions:
{profile['emotions']}

User notes:
{profile['notes']}

Relationship:
{profile['relationship']}

Internet results:
{web_results}

Mood:
{mood}
"""
            }

        ]

        messages += user_memory[user_id]

        # ================== AI RESPONSE ==================

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=messages

        )

        reply = (
            response
            .choices[0]
            .message
            .content
        )

        # ================== SAVE ==================

        user_memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        save_user(user_id, profile)

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "reply": "Something went wrong."
        }), 500

# ================== RUN ==================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
