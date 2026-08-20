# some-agent-like-you

Local memory recall with Mem0 + Ollama + Qdrant.

## Install (CLI + skill)

```shell
uv tool install some-agent-like-you && install-recall-memory-skill
```

This installs `memory_daemon`, `recall-memory`, and copies the packaged skill to:
`~/.agents/skills/recall-memory/SKILL.md`.

## Start runtime

```shell
ollama serve

docker run --name some-agent-like-you-qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v "$HOME/.some_agent_like_you/qdrant:/qdrant/storage" \
  qdrant/qdrant

ollama pull qwen3-embedding:4b

memory_daemon
```

## Recall

```shell
recall-memory --limit 5 "preferred testing conventions"
```

Socket path: `~/.some_agent_like_you/memory.sock`.

## Ingestion

```shell
uv run load_memory
uv run python -m some_agent_like_you.load_memory
uv run load_memory --max-turns-per-chunk 8
```

## hindsight

```shell
docker run -it --pull always --name hindsight --restart unless-stopped -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_PROVIDER=ollama \
  -e HINDSIGHT_API_LLM_MODEL=qwen2.5:14b \
  -v hindsight-data:$HOME/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:0.9.1

uv tool install hindsight-api

export HINDSIGHT_API_LLM_PROVIDER=ollama
export HINDSIGHT_API_LLM_MODEL=qwen2.5:14b
export HINDSIGHT_API_LLM_OLLAMA_NUM_CTX=8192
export HINDSIGHT_API_LLM_TIMEOUT=600
export HINDSIGHT_API_LLM_SEND_BANK_AS_USER=true
export HINDSIGHT_API_LLM_MAX_CONCURRENT=2
export HINDSIGHT_API_RETAIN_MAX_CONCURRENT=2
export HINDSIGHT_API_EMBEDDINGS_LOCAL_ALLOW_MPS=true
export HINDSIGHT_API_RERANKER_LOCAL_ALLOW_MPS=true
export HINDSIGHT_API_RERANKER_LOCAL_FP16=true
export HF_HUB_OFFLINE=1
hindsight-api

npx @vectorize-io/hindsight-coding-agents install copilot-cli --server self-hosted --api-url http://localhost:8888
```
