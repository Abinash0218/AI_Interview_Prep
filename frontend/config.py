import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")


def load_env():
    load_dotenv(ENV_PATH, override=True)


def get_google_client_id() -> str:
    load_env()
    return os.getenv("GOOGLE_CLIENT_ID", "").strip()


def get_frontend_url() -> str:
    load_env()
    return os.getenv("FRONTEND_URL", "http://localhost:8501").strip().rstrip("/")
