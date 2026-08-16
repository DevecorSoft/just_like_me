import sqlite3
from pathlib import Path

COPILOT_DB = Path.home() / ".copilot" / "session-store.db"

def connect():
  conn = sqlite3.connect(f"file:{COPILOT_DB}?mode=ro", uri=True)
  return conn
