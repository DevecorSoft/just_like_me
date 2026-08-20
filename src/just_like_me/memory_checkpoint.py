from pathlib import Path
from datetime import datetime, timezone

JUST_LIKE_ME_DIR = Path.home() / ".just_like_me"
CHECKPOINT_FILE = JUST_LIKE_ME_DIR / "memory_checkpoint.txt"


def read() -> str:
  JUST_LIKE_ME_DIR.mkdir(parents=True, exist_ok=True)
  last_time_stamp = CHECKPOINT_FILE.read_text().strip() \
    if CHECKPOINT_FILE.exists() \
    else "1970-01-01T00:00:00+00:00"
  return last_time_stamp

def check_in(_datetime: datetime) -> str:
  CHECKPOINT_FILE.write_text(_datetime.isoformat())
  return read()
