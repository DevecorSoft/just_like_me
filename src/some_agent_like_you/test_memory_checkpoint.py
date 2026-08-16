from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from unittest import TestCase

from some_agent_like_you.memory_checkpoint import read, check_in

checkpoint = Path.home() / ".some_agent_like_you"
memory_checkpoint_txt_ = checkpoint / "memory_checkpoint.txt"

class Test(TestCase):
  def setUp(self) -> None:
    checkpoint.mkdir(exist_ok=True, parents=True)
    if memory_checkpoint_txt_.exists():
      os.remove(memory_checkpoint_txt_)

  def tearDown(self) -> None:
    if memory_checkpoint_txt_.exists():
      os.remove(memory_checkpoint_txt_)

  def test_read_default(self):
    self.assertEqual("1970-01-01T00:00:00+00:00", read())

  def test_read(self):
    memory_checkpoint_txt_.write_text("1971-01-01T00:00:00+00:00")

    self.assertEqual("1971-01-01T00:00:00+00:00", read())


  def test_check_in(self):
    now = datetime.now(timezone.utc)
    last = check_in(now)
    self.assertEqual(now, datetime.fromisoformat(last))
