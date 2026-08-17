#!/usr/bin/env python3
import json
import logging
import os
from pathlib import Path
import socket
from typing import Any

from huggingface_hub import snapshot_download
import ollama
from mem0 import Memory

from some_agent_like_you.memory_config import config

logger = logging.getLogger(__name__)

MEMORY_SOCKET_PATH = Path.home() / ".some_agent_like_you" / "memory.sock"
RERANKER_REPO = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def _resolve_reranker_model() -> str:
  try:
    return snapshot_download(repo_id=RERANKER_REPO, local_files_only=True)
  except Exception:
    return snapshot_download(repo_id=RERANKER_REPO)

def create_memory_client() -> Memory:
  reranker_model = _resolve_reranker_model()
  memory_config = {
    **config,
    "reranker": {
      "provider": "sentence_transformer",
      "config": {
        "device": "mps",
        "model": reranker_model,
        "local_files_only": True,
      },
    },
  }
  return Memory.from_config(memory_config)


def _prepare_socket(socket_path: Path) -> socket.socket:
  socket_path.parent.mkdir(parents=True, exist_ok=True)
  os.chmod(socket_path.parent, 0o700)

  if socket_path.exists():
    socket_path.unlink()

  server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  server.bind(str(socket_path))
  os.chmod(socket_path, 0o600)
  server.listen()
  return server


def _recv_json(connection: socket.socket) -> dict[str, Any]:
  chunks = []
  while True:
    chunk = connection.recv(4096)
    if not chunk:
      break
    chunks.append(chunk)
    if b"\n" in chunk:
      break
  payload = b"".join(chunks).split(b"\n", 1)[0]
  return json.loads(payload.decode("utf-8"))


def _send_json(connection: socket.socket, payload: dict[str, Any]) -> None:
  wire = json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n"
  connection.sendall(wire)


def _compact_results(raw: Any) -> list[dict[str, Any]]:
  items = raw.get("results", raw) if isinstance(raw, dict) else raw
  if not isinstance(items, list):
    return []
  user_items = [item for item in items if isinstance(item, dict) and item.get("attributed_to") == "user"]
  return [{
    "memory": item.get("memory"),
    "score": item.get("score"),
    "metadata": item.get("metadata"),
  } for item in user_items]


def _handle_connection(connection: socket.socket, memory: Memory) -> None:
  try:
    request = _recv_json(connection)
    query = request["query"]
    limit = request["limit"]

    results = memory.search(
      query=query,
      limit=limit,
      rerank=True,
      filters={"user_id": "some_agent_like_you"},
    )
    _send_json(connection, {"results": _compact_results(results)})
  except Exception as exc:
    _send_json(connection, {"error": str(exc)})


def run_daemon(socket_path: Path = MEMORY_SOCKET_PATH) -> None:
  logger.info("Initializing recall memory client")
  server = _prepare_socket(socket_path)
  memory = create_memory_client()
  ollama.embed(model="qwen3-embedding:4b", input="warmup", keep_alive=-1)
  logger.info("Memory daemon listening on %s", socket_path)

  try:
    with server:
      while True:
        connection, _ = server.accept()
        with connection:
          _handle_connection(connection, memory)
  except KeyboardInterrupt:
    logger.info("Received Ctrl+C, shutting down memory daemon")
  finally:
    if socket_path.exists():
      socket_path.unlink()


def main() -> None:
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
  )
  run_daemon()

if __name__ == "__main__":
  main()
