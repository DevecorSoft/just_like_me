# some-agent-like-you

The memory pipeline uses the Mem0 Python SDK with local Ollama and Qdrant
services. Recall runs through a long-lived, current-user daemon so Mem0, the
Qdrant client, and the CrossEncoder reranker stay warm.

## Start the runtime

```shell
# Start these only if they are not already running.
ollama serve
docker run --name some-agent-like-you-qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v "$HOME/.some_agent_like_you/qdrant:/qdrant/storage" \
  qdrant/qdrant
```

Pull and pin the embedding model in Ollama, then start the recall daemon:

```shell
ollama pull qwen3-embedding:4b
curl http://127.0.0.1:11434/api/embed \
  -d '{"model":"qwen3-embedding:4b","input":"warmup","keep_alive":-1}'

uv run recall-daemon
```

Do not use `ollama run` for the warmup: embedding-only models generally do not
support text generation. The daemon repeats the `keep_alive=-1` embed request
after every query because Mem0's current Ollama wrapper sends ordinary embed
requests without a keep-alive value.

In another terminal, recall is a lightweight Unix-socket JSON request:

```shell
uv run recall-memory --limit 5 "preferred testing conventions"
```

The socket defaults to `~/.some_agent_like_you/recall.sock`. Its parent
directory is mode `0700` and the socket is mode `0600`.

Verify or stop model residency with:

```shell
ollama ps
ollama stop qwen3-embedding:4b
```

Run the ingestion pipeline separately when needed:

```shell
uv run python -m some_agent_like_you.load_memory
```

Changing the embedding model or dimensions requires a new Qdrant collection
because an existing collection keeps its original vector dimensions.