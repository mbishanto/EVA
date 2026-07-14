import os
import logging

from app import create_app

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO"), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
