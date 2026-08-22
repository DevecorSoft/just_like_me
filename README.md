# just-like-me

A local behavior-evolution control plane for GitHub Copilot CLI, powered by Hindsight.

Hindsight owns cognition (retain → recall → observations → reflect). This project owns behavioral governance (propose → eval → approve → publish → monitor → rollback).

## Install

```shell
uv tool install just-like-me
just_like_me.skills.install
```

Copies the packaged skill to `~/.agents/skills/recall-memory/SKILL.md`.

## Start Hindsight

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
```

Or install as a macOS daemon (runs on login, auto-restarts):

```shell
just_like_me.daemon.install
```

## Copilot integration

```shell
npx @vectorize-io/hindsight-coding-agents install copilot-cli --server self-hosted --api-url http://localhost:8888
```

## Ingestion

Ingest Copilot conversation history into the `just_like_me` memory bank:

```shell
just_like_me.load_memory
just_like_me.load_memory --max-turns-per-chunk 10
```

Reads from the read-only Copilot SQLite session store, checkpoints progress, and retains conversations via the Hindsight client at `http://localhost:8888`.

## Recall

```shell
hindsight memory recall just_like_me "<semantic query>" --fact-type world,observation --budget mid
```

## References

- [Hindsight](https://github.com/vectorize-io/hindsight)
- [Hindsight Recall API](https://hindsight.vectorize.io/developer/api/recall)
- [Hindsight Copilot integration](https://hindsight.vectorize.io/blog/2026/07/30/github-copilot-persistent-memory)

