# just-like-me

Local memory recall with Mem0 + Ollama + Qdrant.

## Install (CLI + skill)

```shell
uv tool install just-like-me && install-recall-memory-skill
```

This installs `memory_daemon`, `recall-memory`, and copies the packaged skill to:
`~/.agents/skills/recall-memory/SKILL.md`.

## Start runtime

```shell
ollama serve

docker run --name just-like-me-qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v "$HOME/.just_like_me/qdrant:/qdrant/storage" \
  qdrant/qdrant

ollama pull qwen3-embedding:4b

memory_daemon
```

## Recall

```shell
recall-memory --limit 5 "preferred testing conventions"
```

Socket path: `~/.just_like_me/memory.sock`.

## Ingestion

```shell
uv run load_memory
uv run python -m just_like_me.load_memory
uv run load_memory --max-turns-per-chunk 8
```

## hindsight

```shell
uv tool install hindsight-api

export HINDSIGHT_API_LLM_PROVIDER=ollama
export HINDSIGHT_API_LLM_MODEL=muse-glimmer:30b-mlx
export HINDSIGHT_API_LLM_TIMEOUT=1200
export HINDSIGHT_API_REFLECT_WALL_TIMEOUT=1200
export HINDSIGHT_API_LLM_SEND_BANK_AS_USER=true
export HINDSIGHT_API_LLM_MAX_CONCURRENT=1
export HINDSIGHT_API_RETAIN_MAX_CONCURRENT=1
export HF_HUB_OFFLINE=1
hindsight-api

npx @vectorize-io/hindsight-coding-agents install copilot-cli --server self-hosted --api-url http://localhost:8888
```
