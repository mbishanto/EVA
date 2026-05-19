from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import random

app = Flask(__name__)

# CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# ================= GROQ KEYS =================

groq_keys = os.getenv("GROQ_KEYS", "")

GROQ_KEYS = groq_keys.split(",") if groq_keys else []

if not GROQ_KEYS:
    raise ValueError("Missing GROQ_KEYS")

# ================= HOME =================

@app.route("/")
def home():
    return "Backend Running"

# ================= CHAT =================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data["message"]

    # RANDOM API KEY
    api_key = random.choice(GROQ_KEYS)

    try:

        client = Groq(
            api_key=api_key
        )

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]

        )

        reply = response.choices[0].message.content

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "reply": "AI server busy right now."
        }), 500

# ================= RUN =================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
