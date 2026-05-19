from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)

CORS(app)

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data["message"]

    response = model.generate_content(user_message)

    return jsonify({
        "reply": response.text
    })

@app.route("/")
def home():
    return "Backend Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
