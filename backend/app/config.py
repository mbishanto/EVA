import os


def _parse_frontend_urls(raw):
    """
    Parse the FRONTEND_URL environment variable into a list of allowed origins.

    Supports comma-separated domains:
        FRONTEND_URL=https://eva-me.vercel.app,https://eva-ai.vercel.app

    To add a new frontend domain, simply append it to the comma-separated list
    in the FRONTEND_URL environment variable. No code changes are needed.
    """
    if not raw:
        return None
    return [u.strip().rstrip("/") for u in raw.split(",") if u.strip()]


DEV_FRONTEND_URLS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


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

    # ------------------------------------------------------------------
    # CORS: Frontend allowed origins
    # ------------------------------------------------------------------
    # Set FRONTEND_URL to one or more comma-separated origins:
    #   FRONTEND_URL=https://eva-me.vercel.app,https://eva-ai.vercel.app
    #
    # To allow an additional domain, add it to the list — no code changes needed.
    # ------------------------------------------------------------------
    _raw_frontend = os.getenv("FRONTEND_URL")
    FRONTEND_URLS = _parse_frontend_urls(_raw_frontend)

    if FRONTEND_URLS is None:
        if ENV == "production":
            raise RuntimeError(
                "FRONTEND_URL environment variable is required in production. "
                "Set it to one or more comma-separated frontend origins, e.g.:\n"
                "  FRONTEND_URL=https://eva-me.vercel.app,https://eva-ai.vercel.app"
            )
        FRONTEND_URLS = DEV_FRONTEND_URLS

    if not GROQ_KEYS:
        raise RuntimeError("Missing GROQ_KEYS environment variable")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
