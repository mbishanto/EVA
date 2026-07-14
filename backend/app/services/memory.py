from datetime import datetime


class MemoryService:
    def detect_mood(self, text):
        text = text.lower()
        if any(w in text for w in ["sad", "depressed", "tired", "lonely", "heartbroken"]):
            return "sad"
        if any(w in text for w in ["error", "problem", "issue", "broken", "bug"]):
            return "frustrated"
        if any(w in text for w in ["happy", "excited", "amazing", "wonderful", "great"]):
            return "happy"
        if any(w in text for w in ["angry", "mad", "annoyed", "furious"]):
            return "angry"
        return "normal"

    def get_time_context(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 18:
            return "afternoon"
        if 18 <= hour < 24:
            return "evening"
        return "night"

    def extract_name(self, text):
        import re
        match = re.search(
            r"(my name is|i am|i'm|call me)\s+([A-Za-z ]+)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(2).strip().split()[0]
        return None

    def merge_memory_data(self, profile, memory_text):
        import json
        import re

        try:
            cleaned = re.sub(r"```json|```", "", memory_text).strip()
            memory_data = json.loads(cleaned)
        except (json.JSONDecodeError, AttributeError):
            return profile

        for note in memory_data.get("notes", []):
            if note not in profile["notes"]:
                profile["notes"].append(note)

        for topic in memory_data.get("favorite_topics", []):
            if topic not in profile["relationship"]["favorite_topics"]:
                profile["relationship"]["favorite_topics"].append(topic)

        if memory_data.get("summary"):
            profile["summary"] = memory_data["summary"]

        emotion = memory_data.get("emotion")
        if emotion and emotion not in profile["emotions"]:
            profile["emotions"].append(emotion)

        return profile


memory_service = MemoryService()
