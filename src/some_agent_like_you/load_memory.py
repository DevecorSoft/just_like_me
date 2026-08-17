#!/usr/bin/env python3
import logging
import time
from datetime import datetime, timezone
from itertools import groupby

from mem0 import Memory

from some_agent_like_you import memory_checkpoint
from some_agent_like_you.session_store_query import connect

logger = logging.getLogger(__name__)

def create_local_memory() -> Memory:
  config = {
    "vector_store": {
      "provider": "qdrant",
      "config": {"host": "localhost", "port": 6333,
                 "embedding_model_dims": 2560,
                 "collection_name": "some_agent_like_you", },
    },
    "llm": {
      "provider": "ollama",
      "config": {
        "model": "qwen2.5:14b",
        "temperature": 0.1,
        "max_tokens": 2048,
      },
    },
    "embedder": {
      "provider": "ollama",
      "config": {"model": "qwen3-embedding:4b", "embedding_dims": 2560},
    },
  }
  return Memory.from_config(config)


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

  messages_generator = context_aware_conversation_generator(rows,
                                                            max_turns_per_chunk)

  initialization_started_at = time.perf_counter()
  logger.info("Initializing local Mem0 client")
  memory_client = create_local_memory()
  logger.info(
    "Initialized local Mem0 client in %.1fs",
    time.perf_counter() - initialization_started_at
  )
  pipeline_started_at = time.perf_counter()
  processed_batches = 0
  for batch_index, (session_id, messages) in enumerate(
    messages_generator,
    start=1
  ):
    batch_started_at = time.perf_counter()
    logger.info(
      "Starting memory batch %d: session_id=%s messages=%d",
      batch_index,
      session_id,
      len(messages)
    )
    memory_client.add(
      messages,
      user_id="some_agent_like_you",
      metadata={
        "source": "cron_memory_pipeline",
        "session_id": session_id
      }
    )

    processed_batches = batch_index
    logger.info(
      "Completed memory batch %d in %.1fs: session_id=%s",
      batch_index,
      time.perf_counter() - batch_started_at,
      session_id
    )

  memory_checkpoint.check_in(check_in_time)
  logger.info(
    "Memory pipeline completed: batches=%d elapsed=%.1fs",
    processed_batches,
    time.perf_counter() - pipeline_started_at
  )


if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
  )
  run_memory_pipeline(max_turns_per_chunk=10)
