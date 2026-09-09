# just-like-me

Local tooling that makes GitHub Copilot CLI more like you, powered by Hindsight.

Hindsight owns cognition (retain → recall → observations → mental models). This project
owns the last-mile engineering: local runtime management, historical ingestion, and
instruction publication. The next step is personal discernment assistance through
user-confirmed Hindsight Documents, scoped recall, and a decision Skill (see
blueprint.md); this workflow is not yet implemented.

## Install

```shell
uv tool install .
just_like_me.skills.install
just_like_me.instructions.install
```

- `just_like_me.skills.install`: Installs `recall-discernment` to
  `~/.agents/skills/recall-discernment/SKILL.md` to recall decisions, reasons and applicability limits.
- `just_like_me.instructions.install`: Combines the packaged `instructions.md`
  discernment content with the shared execution rules and installs the result to
  `~/.copilot/instructions/just-like-me-instructions.md`, without accessing Hindsight.

## Local LLM

Deploy a local OpenAI-compatible LLM endpoint with [mtplx](https://mtplx.com/) (the
config below expects it at `http://localhost:8000/v1`).

## Start Hindsight

```shell
docker volume create hindsight_pgdata

docker run -d \
  --name hindsight-postgres \
  --restart unless-stopped \
  -p 15432:5432 \
  -e POSTGRES_DB=hindsight \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -v hindsight_pgdata:/var/lib/postgresql/data \
  pgvector/pgvector:pg16
```

```shell
uv tool install hindsight-api

export HINDSIGHT_API_LLM_PROVIDER=openai
export HINDSIGHT_API_LLM_API_KEY=1
export HINDSIGHT_API_LLM_BASE_URL=http://localhost:8000/v1
export HINDSIGHT_API_LLM_MODEL=mtplx-qwen35-9b-optimized-speed
export HINDSIGHT_API_LLM_TIMEOUT=1200
export HINDSIGHT_API_REFLECT_WALL_TIMEOUT=1200
export HINDSIGHT_API_LLM_SEND_BANK_AS_USER=true
export HINDSIGHT_API_LLM_MAX_CONCURRENT=1
export HINDSIGHT_API_RETAIN_MAX_CONCURRENT=1
export HINDSIGHT_API_DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:15432/hindsight
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

## Ingestion & Instructions Update

Configure Hindsight to reconstruct your discernment with office-friendly defaults for a
36 GB Mac, replacing the configured bank fields and overwriting
`~/.hindsight/coding-agent.json`:

```shell
just_like_me.install
```

Ingest Copilot conversation history into the `just_like_me` memory bank:

```shell
just_like_me.load_memory
just_like_me.load_memory --max-turns-per-chunk 10
```

Reads from the read-only Copilot SQLite session store, checkpoints progress, and
retains conversations via the Hindsight client at `http://localhost:8888`.

Update personal instructions from Hindsight Mental Model:

```shell
just_like_me.instructions.update
```

Publishes conditional decision patterns from the `just_like_me_discernment` Mental
Model to `~/.copilot/instructions/just-like-me-instructions.md`, creating the model
with automatic refresh if absent and using evidence-first defaults until content is
available.

`instructions.update` refreshes only the discernment content in `instructions.md`,
then calls `instructions.install`. Both commands publish the same execution rules,
defined once in `instructions.py`.

## Recall

```shell
hindsight memory recall just_like_me "<semantic query>" --fact-type world,observation --budget mid
```

## References

- [Hindsight](https://github.com/vectorize-io/hindsight)
- [Hindsight Recall API](https://hindsight.vectorize.io/developer/api/recall)
- [Hindsight Copilot integration](https://hindsight.vectorize.io/blog/2026/07/30/github-copilot-persistent-memory)
