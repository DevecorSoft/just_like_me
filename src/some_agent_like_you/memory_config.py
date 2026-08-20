hindsight_config = {
  "base_url": "http://localhost:8888",
  "bank_id": "some_agent_like_you",
}

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
