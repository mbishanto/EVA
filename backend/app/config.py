import os


class Config:
    GROQ_KEYS = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

    MAX_HISTORY = int(os.getenv("MAX_HISTORY", "1000"))
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "30"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))

    KEY_RETRY_LIMIT = int(os.getenv("KEY_RETRY_LIMIT", "3"))
    KEY_COOLDOWN_SECONDS = int(os.getenv("KEY_COOLDOWN_SECONDS", "300"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENV = os.getenv("ENV", "production")

    if not GROQ_KEYS:
        raise ValueError("Missing GROQ_KEYS environment variable")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
