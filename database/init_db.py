"""
Initialize database tables.
Run from project root: python database/init_db.py
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from backend.database.connection import init_db

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")
