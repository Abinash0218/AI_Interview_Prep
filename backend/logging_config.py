import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging():
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    app_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=5_000_000,
        backupCount=5,
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)

    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "error.log"),
        maxBytes=5_000_000,
        backupCount=5,
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    auth_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "auth.log"),
        maxBytes=2_000_000,
        backupCount=3,
    )
    auth_handler.setFormatter(formatter)
    auth_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(app_handler)
    root.addHandler(error_handler)

    auth_logger = logging.getLogger("auth")
    auth_logger.addHandler(auth_handler)
    auth_logger.setLevel(logging.INFO)
