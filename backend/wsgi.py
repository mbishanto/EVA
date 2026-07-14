"""
EVA AI — Flask Application Entry Point

Single entry point for both:
  - Production:  gunicorn wsgi:app
  - Development: python wsgi.py

Exports a single ``app`` object (Flask application factory pattern).
"""

import os
import sys
import logging

# ---------------------------------------------------------------------------
# 1. Bootstrap logging — available before create_app()
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO"), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("eva.startup")

# ---------------------------------------------------------------------------
# 2. Validate required environment variables before importing the app factory
# ---------------------------------------------------------------------------
_missing = []

if not os.getenv("GROQ_KEYS"):
    _missing.append("GROQ_KEYS")
if not os.getenv("SUPABASE_URL"):
    _missing.append("SUPABASE_URL")
if not os.getenv("SUPABASE_KEY"):
    _missing.append("SUPABASE_KEY")

if _missing:
    raise RuntimeError(
        "Cannot start EVA backend — the following required environment "
        "variable(s) are not set:\n"
        + "\n".join(f"  - {name}" for name in _missing)
        + "\n\nSet them in the environment or in a .env file before starting."
    )

# ---------------------------------------------------------------------------
# 3. Import and create the application
# ---------------------------------------------------------------------------
from app import create_app  # noqa: E402

app = create_app()

# ---------------------------------------------------------------------------
# 4. Startup summary
# ---------------------------------------------------------------------------
import flask  # noqa: E402
python_version = sys.version.split()[0]  # noqa: E402

has_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
has_groq = bool(os.getenv("GROQ_KEYS"))

logger.info("=" * 56)
logger.info("  EVA AI Backend — started successfully")
logger.info("=" * 56)
logger.info("  Environment      : %s", app.config.get("ENV", "unknown"))
logger.info("  Flask version    : %s", flask.__version__)
logger.info("  Python version   : %s", python_version)
logger.info("  Supabase config  : %s", "detected" if has_supabase else "MISSING")
logger.info("  Groq API keys    : %s", "detected" if has_groq else "MISSING")
logger.info("  AI model         : %s", app.config.get("GROQ_MODEL", "unknown"))
logger.info("  Allowed origins  : %s", app.config.get("FRONTEND_URLS", []))
logger.info("  Log level        : %s", os.getenv("LOG_LEVEL", "INFO"))
logger.info("-" * 56)

# ---------------------------------------------------------------------------
# 5. Local development server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info("  Starting dev server on 0.0.0.0:%d", port)
    logger.info("=" * 56)
    app.run(host="0.0.0.0", port=port)
