from pathlib import Path
from datetime import datetime, timezone

SOME_AGENT_LIKE_YOU_DIR = Path.home() / ".some_agent_like_you"
CHECKPOINT_FILE = SOME_AGENT_LIKE_YOU_DIR / "memory_checkpoint.txt"


def read() -> str:
  SOME_AGENT_LIKE_YOU_DIR.mkdir(parents=True, exist_ok=True)
  last_time_stamp = CHECKPOINT_FILE.read_text().strip() \
    if CHECKPOINT_FILE.exists() \
    else "1970-01-01T00:00:00+00:00"
  return last_time_stamp

def check_in(_datetime: datetime) -> str:
  CHECKPOINT_FILE.write_text(_datetime.isoformat())
  return read()
