# some-agent-like-you

The memory pipeline uses the Mem0 Python SDK directly. It does not require a
Mem0 server or a separate Qdrant server: the vector store and history database
are persisted locally under `~/.some_agent_like_you/mem0`.

Ollama must be installed and running locally for both the LLM and embedding
model:

```shell
ollama pull qwen3:4b
ollama pull nomic-embed-text
uv run python -m some_agent_like_you.load_memory
```

The local configuration can be customized with environment variables:

| Variable | Default |
| --- | --- |
| `MEM0_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` |
| `MEM0_LLM_MODEL` | `qwen3:4b` |
| `MEM0_EMBEDDING_MODEL` | `nomic-embed-text` |
| `MEM0_EMBEDDING_DIMS` | `768` |
| `MEM0_DATA_DIR` | `~/.some_agent_like_you/mem0` |

Changing the embedding model or its dimensions requires a new `MEM0_DATA_DIR`
because an existing Qdrant collection keeps its original vector dimensions.