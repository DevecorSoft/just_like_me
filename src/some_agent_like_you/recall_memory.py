#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import socket
from typing import Any

from some_agent_like_you.memory_daemon import MEMORY_SOCKET_PATH


def _check_socket_available(socket_path: Path) -> None:
  if not socket_path.exists():
    raise SystemExit(f"memory daemon socket not found: {socket_path}")
  if not socket_path.is_socket():
    raise SystemExit(f"memory daemon socket is invalid: {socket_path}")


def _send_request(socket_path: Path, query: str, limit: int) -> dict[str, Any]:
  request = json.dumps({"query": query, "limit": limit}, ensure_ascii=False)
  with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
    client.connect(str(socket_path))
    client.sendall(request.encode("utf-8") + b"\n")
    chunks = []
    while True:
      chunk = client.recv(4096)
      if not chunk:
        break
      chunks.append(chunk)
      if b"\n" in chunk:
        break
  wire = b"".join(chunks).split(b"\n", 1)[0]
  return json.loads(wire.decode("utf-8"))


def main() -> None:
  parser = argparse.ArgumentParser(description="Recall memory via local daemon")
  parser.add_argument("query")
  parser.add_argument("--limit", type=int, required=True)
  args = parser.parse_args()

  _check_socket_available(MEMORY_SOCKET_PATH)
  response = _send_request(MEMORY_SOCKET_PATH, args.query, args.limit)
  if "error" in response:
    raise SystemExit(response["error"])
  print(json.dumps(response["results"], ensure_ascii=False))


if __name__ == "__main__":
  main()
