#!/usr/bin/env python3
from datetime import datetime, timezone
from itertools import groupby

from mem0 import Memory

from some_agent_like_you import memory_checkpoint
from some_agent_like_you.session_store_query import connect


def context_aware_conversation_generator(turns, max_turns_per_chunk=10):
  valid_turns = filter(
    lambda i: i["user_message"] is not None,
    turns)

  valid_turns = sorted(valid_turns, key=lambda r: r["session_id"])
  for session_id, _group in groupby(valid_turns, lambda r: r["session_id"]):
    group = list(
      map(
        lambda
          i: f"<user>{i["user_message"]}</user>\n<assistant>"
             f"{i["assistant_response"]}</assistant>",
        _group)
    )
    for i in range(0, len(group), max_turns_per_chunk):
      chunk = group[i: i + max_turns_per_chunk]
      text_block = "\n".join(chunk)

      yield session_id, text_block


def run_memory_pipeline(max_turns_per_chunk: int):
  last_timestamp = memory_checkpoint.read()
  conn = connect()
  cursor = conn.cursor()
  cursor.execute("""
                 SELECT session_id, turn_index, user_message, assistant_response
                 FROM turns
                 WHERE timestamp > ?
                 ORDER BY timestamp ASC
                 """, (last_timestamp,))
  rows = map(
    lambda i: dict(session_id=i[0], user_message=i[2], assistant_response=i[3]),
    cursor.fetchall())
  conn.close()

  check_in_time = datetime.now(timezone.utc)

  text_block_generator = context_aware_conversation_generator(rows,
                                                              max_turns_per_chunk)

  memory_client = Memory()
  for session_id, text_block in text_block_generator:
    memory_client.add(
      text_block,
      user_id="some_agent_like_you",
      metadata={
        "source": "cron_memory_pipeline",
        "session_id": session_id
      }
    )

  memory_checkpoint.check_in(check_in_time)

if __name__ == "__main__":
  run_memory_pipeline(max_turns_per_chunk=10)
