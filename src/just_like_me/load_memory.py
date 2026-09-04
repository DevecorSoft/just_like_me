#!/usr/bin/env python3
import argparse
import json
import logging
import time
from datetime import datetime, timezone
from itertools import groupby

from hindsight_client import Hindsight

from just_like_me import memory_checkpoint
from just_like_me.session_store_query import connect

logger = logging.getLogger(__name__)

def context_aware_conversation_generator(turns, max_turns_per_chunk=10):
  valid_turns = filter(
    lambda i: i["user_message"] is not None and i["assistant_response"] is not None,
    turns)

  valid_turns = sorted(valid_turns, key=lambda r: r["session_id"])
  for session_id, _group in groupby(valid_turns, lambda r: r["session_id"]):
    group = list(
      map(
        lambda i: [{"role": "user", "content": i["user_message"]},
                   {"role": "assistant", "content": i["assistant_response"]}],
        _group)
    )
    for i in range(0, len(group), max_turns_per_chunk):
      chunk = group[i: i + max_turns_per_chunk]

      yield session_id, [k for j in chunk for k in j]


def run_memory_pipeline(max_turns_per_chunk):
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

  messages_generator = context_aware_conversation_generator(rows,
                                                            max_turns_per_chunk)

  base_url = "http://localhost:8888"
  logger.info("Initializing Hindsight client: %s", base_url)
  memory_client = Hindsight(base_url=base_url, timeout=1200)
  bank_id = "just_like_me"
  pipeline_started_at = time.perf_counter()
  processed_batches = 0

  try:
    for batch_index, (session_id, messages) in enumerate(
      messages_generator,
      start=1
    ):
      batch_started_at = time.perf_counter()
      raw_messages = json.dumps(messages)
      logger.info(
        "Starting memory batch %d: session_id=%s messages_size=%s",
        batch_index,
        session_id,
        ", ".join([str(len(messages)),str(len(raw_messages))])
      )
      memory_client.retain(
        bank_id=bank_id,
        content=raw_messages,
        context=f"coding agent conversation, session {session_id}",
        document_id=f"{session_id}#chunk-{batch_index}",
        metadata={
          "source": "cron_memory_pipeline",
          "session_id": session_id
        },
        tags=[
          "source:cron-pipeline",
          "project:just_like_me",
          "env:work",
          "memory:history"
        ],
        retain_async=False,
      )

      processed_batches = batch_index
      logger.info(
        "Completed memory batch %d in %.1fs: session_id=%s",
        batch_index,
        time.perf_counter() - batch_started_at,
        session_id
      )
  finally:
    memory_client.close()

  memory_checkpoint.check_in(check_in_time)
  logger.info(
    "Memory pipeline completed: batches=%d elapsed=%.1fs",
    processed_batches,
    time.perf_counter() - pipeline_started_at
  )


def main() -> None:
  parser = argparse.ArgumentParser(description="Load conversation history into memory store")
  parser.add_argument(
    "--max-turns-per-chunk",
    type=int,
    default=2,
    help="Maximum number of turns to process in one memory batch (default: 2)",
  )
  args = parser.parse_args()

  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
  )
  run_memory_pipeline(max_turns_per_chunk=args.max_turns_per_chunk)


if __name__ == "__main__":
  main()
