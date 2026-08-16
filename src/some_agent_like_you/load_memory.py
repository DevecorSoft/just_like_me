#!/usr/bin/env python3
from datetime import datetime, timezone
from itertools import groupby

from mem0 import Memory

from some_agent_like_you import memory_checkpoint
from some_agent_like_you.session_store_query import connect


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
        "model": "muse-glimmer:30b-mlx",
        "temperature": 0.1,
        "max_tokens": 128000,
      },
    },
    "embedder": {
      "provider": "ollama",
      "config": {"model": "qwen3-embedding:4b", "embedding_dims": 2560},
    },
    "reranker": {
      "provider": "sentence_transformer",
      "config": {
        "device": "mps",
        "model": "cross-encoder/ms-marco-MiniLM-L-6-v2"
      }
    },
  }
  return Memory.from_config(config)


def context_aware_conversation_generator(turns, max_turns_per_chunk=10):
  valid_turns = filter(
    lambda i: i["user_message"] is not None,
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

  memory_client = create_local_memory()
  for session_id, messages in messages_generator:
    memory_client.add(
      messages,
      user_id="some_agent_like_you",
      metadata={
        "source": "cron_memory_pipeline",
        "session_id": session_id
      }
    )

  memory_checkpoint.check_in(check_in_time)


if __name__ == "__main__":
  run_memory_pipeline(max_turns_per_chunk=10)
