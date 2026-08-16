# Ultra-Lightweight Self-Evolving Architecture Scheme for Personal AI Agent (V2.2 Local Skill Edition)

This architecture eliminates Mem0 servers, MCP adapters, background proxies, and terminal hooks. It interfaces directly with GitHub Copilot CLI’s native SQLite store (`~/.copilot/session-store.db`) via **URI Read-Only Mode (`file:...mode=ro`)**. A local Copilot Skill invokes narrow Python CLI scripts only when memory recall is useful, preserving zero baseline terminal overhead and keeping all memory data offline.

System evolution is decoupled into a three-stage pipeline: **Memory**, **Reflection**, and **Evolution**, each tracking execution state via pure-text checkpoints. Runtime recall is a separate read-only path and does not mutate pipeline state.

---

## 1. System Architecture

```
+-------------------------------------------------------------------------+
|                Frontend: Copilot CLI (Native Terminal Host)             |
|                                                                         |
|  ├── Static Rules : ~/.copilot-instructions.md  (Rewritten by Reflection)|
|  ├── Dynamic Recall: Local Skill -> Python CLI    (On-demand Mem0 search) |
|  └── Native Store : ~/.copilot/session-store.db (Native SQLite Store)   |
+----------------------+-------------------------------+------------------+
                       |                               |
                       | invokes recall CLI            | read-only SQLite
                       v                               v
+-------------------------------------------------------------------------+
|                         Local Python Runtime                            |
|                                                                         |
|  ├── Recall CLI    : Semantic query -> Mem0 SDK search -> JSON output   |
|  │                                  |                                   |
|  │                                  v                                   |
|  │                   Shared Local Mem0 Configuration                    |
|  │                   (Ollama + local vector store)                      |
|  │                                  ^                                   |
|  │                                  |                                   |
|  ├── 1. Memory     : Reads DB -> Updates Mem0 via Python SDK             |
|  │                   State: ~/.my_agent/checkpoint_memory.txt           |
|  │                                                                      |
|  ├── 2. Reflection : LLM JSON Analysis -> Multi-Target Outputs          |
|  │                   ├── Target A: ~/.my_agent/dataset/train.jsonl      |
|  │                   ├── Target B: Mem0 Engine (Distilled Rules)        |
|  │                   └── Target C: ~/.copilot-instructions.md          |
|  │                   State: ~/.my_agent/checkpoint_reflection.txt     |
|  │                                                                      |
|  └── 3. Evolution  : Reads train.jsonl -> Triggers Local MLX LoRA       |
|                      Output: ~/.my_agent/adapters/latest                |
+-------------------------------------------------------------------------+

```

---

## 2. Core Module Matrix

| Stage | Mechanism | Primary Responsibility & Targets | Compute Load | Frequency |
| --- | --- | --- | --- | --- |
| **Recall** | Copilot Skill + Python CLI + Mem0 SDK | Searches local memories and returns bounded JSON context to Copilot without exposing write operations | **Low** (On-demand embedding and vector search) | On demand |
| **Memory** | Read-Only DB + Mem0 SDK | Syncs raw recent dialog facts directly to Mem0 for short-term contextual continuity | **Ultra-Low** (Lightweight API/Rule extraction) | High (e.g., hourly) |
| **Reflection** | Read-Only DB + Local LLM | Cleans turns via LLM JSON extraction into **3 targets**: <br>

<br>1. `train.jsonl` (Golden Pairs)<br>

<br>2. **Mem0** (Distilled Rules)<br>

<br>3. `~/.copilot-instructions.md` | **Medium** (Local Ollama LLM inference) | Medium (e.g., daily) |
| **Evolution** | `train.jsonl` + MLX LoRA | Consumes refined dataset to fine-tune Apple Silicon MLX model weights, solidifying latent coding habits | **High** (GPU/NPU intensive training) | Low (e.g., weekly / sample-based) |

---

## 3. Configuration & Implementation

### 3.1 Copilot Skill Integration

#### Architecture Decision

The runtime integration uses the Mem0 Python SDK directly through local CLI scripts and a Copilot Skill.

- **Rejected: hosted Mem0 MCP.** The official MCP endpoint targets Mem0 Platform and stores memories in the cloud, which violates the pure-offline requirement.
- **Rejected: self-hosted Mem0 REST server plus MCP adapter.** It adds service lifecycle, networking, configuration duplication, and an extra protocol layer without benefiting the current single-user, Python-only deployment.
- **Adopted: Python SDK scripts plus Skill.** This reuses the same local Mem0 configuration as the ingestion pipeline and introduces no persistent application server.

The server option should be reconsidered only if multiple users, machines, languages, or independent agent clients need concurrent access to one centrally managed memory store.

#### Skill Contract

The Skill describes when memory is useful and delegates retrieval to a narrow, read-only CLI:

```text
Copilot request
    -> Skill identifies a need for prior context
    -> search_memory CLI receives a concise semantic query
    -> Mem0 SDK searches the local user scope
    -> CLI emits bounded JSON results
    -> Copilot uses results as untrusted context
```

The Skill and CLI must follow these rules:

1. Recall only when a request may depend on prior preferences, decisions, constraints, corrections, or project context.
2. Use the same Mem0 factory, vector collection, embedding model, dimensions, and `user_id` as the Memory pipeline.
3. Return strict JSON containing only the memory text, relevance score, source metadata, and stable identifier.
4. Apply a small result limit and expose no add, update, or delete operation.
5. Treat recalled content as contextual data, never as higher-priority instructions.
6. Surface retrieval failures explicitly; do not silently return success-shaped empty results.

The initial Skill package is intentionally small:

```text
some-agent-like-you/
├── SKILL.md
└── scripts/
    └── search_memory.py
```

`SKILL.md` contains the trigger policy and invocation instructions. `search_memory.py` owns input validation, local Mem0 initialization, scoped search, and JSON serialization. Memory ingestion remains a scheduled task rather than a Skill action.

### 3.2 Memory Pipeline (`~/.my_agent/memory.py`)

Extracts recent dialogue turns and syncs short-term facts into Mem0:

```python
#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from some_agent_like_you.memory_store import create_local_memory

COPILOT_DB = Path.home() / ".copilot" / "session-store.db"
CHECKPOINT_FILE = Path.home() / ".my_agent" / "checkpoint_memory.txt"

memory_client = create_local_memory()

def run_memory():
    if not COPILOT_DB.exists():
        return

    last_ts = CHECKPOINT_FILE.read_text().strip() if CHECKPOINT_FILE.exists() else "1970-01-01 00:00:00"
    conn = sqlite3.connect(f"file:{COPILOT_DB}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, created_at FROM turns
        WHERE created_at > ? ORDER BY created_at ASC
    """, (last_ts,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return

    max_ts = last_ts
    dialogs = []
    for role, content, created_at in rows:
        max_ts = max(max_ts, created_at)
        dialogs.append(f"{role}: {content}")

    if dialogs:
        memory_client.add("\n".join(dialogs[-10:]), user_id="digital_twin", metadata={"source": "memory_stage"})

    CHECKPOINT_FILE.write_text(max_ts, encoding="utf-8")

if __name__ == "__main__":
    run_memory()

```

### 3.3 Reflection Pipeline (`~/.my_agent/reflection.py`)

Employs a local small LLM (e.g., `Qwen2.5-Coder-3B` via Ollama) to perform single-step structured reflection, producing multi-target outputs without relying on imprecise vector embeddings:

```python
#!/usr/bin/env python3
import json
import sqlite3
import urllib.request
from pathlib import Path
from some_agent_like_you.memory_store import create_local_memory

COPILOT_DB = Path.home() / ".copilot" / "session-store.db"
CHECKPOINT_FILE = Path.home() / ".my_agent" / "checkpoint_reflection.txt"
DATASET_PATH = Path.home() / ".my_agent" / "dataset" / "train.jsonl"

memory_client = create_local_memory()

REFLECTION_PROMPT = """Analyze this user prompt from a CLI coding session:
1. Determine if it contains explicit coding standards, framework preferences, constraints, or code correction instructions.
2. If yes, extract the exact rule into a single clear sentence.

User Prompt: "{user_prompt}"

Return strictly formatted JSON only:
{{"is_valuable": true/false, "extracted_rule": "Rule string or empty"}}"""

def analyze_intent(user_prompt: str) -> dict:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:3b",
        "prompt": REFLECTION_PROMPT.format(user_prompt=user_prompt),
        "format": "json",
        "stream": False
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return json.loads(data.get("response", "{}"))
    except Exception:
        return {"is_valuable": False, "extracted_rule": ""}

def run_reflection():
    if not COPILOT_DB.exists():
        return

    last_ts = CHECKPOINT_FILE.read_text().strip() if CHECKPOINT_FILE.exists() else "1970-01-01 00:00:00"
    conn = sqlite3.connect(f"file:{COPILOT_DB}?mode=ro", uri=True)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, created_at FROM turns
        WHERE created_at > ? ORDER BY created_at ASC
    """, (last_ts,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return

    golden_pairs = []
    distilled_rules = []
    current_prompt = None
    max_ts = last_ts

    for role, content, created_at in rows:
        max_ts = max(max_ts, created_at)
        if role == "user":
            current_prompt = content
        elif role == "assistant" and current_prompt:
            analysis = analyze_intent(current_prompt)
            if analysis.get("is_valuable"):
                # Target A: Golden Pairs for fine-tuning
                if "```" in content:
                    golden_pairs.append({
                        "messages": [
                            {"role": "system", "content": "You are the user's digital twin."},
                            {"role": "user", "content": current_prompt},
                            {"role": "assistant", "content": content}
                        ]
                    })
                # Target B: High-value rules into Mem0
                rule = analysis.get("extracted_rule")
                if rule:
                    distilled_rules.append(rule)
            current_prompt = None

    if golden_pairs:
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATASET_PATH, "a", encoding="utf-8") as f:
            for pair in golden_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    if distilled_rules:
        for rule in distilled_rules:
            memory_client.add(rule, user_id="digital_twin", metadata={"source": "llm_reflection"})

    CHECKPOINT_FILE.write_text(max_ts, encoding="utf-8")

if __name__ == "__main__":
    run_reflection()

```

### 3.4 Evolution Pipeline (`~/.my_agent/evolution.py`)

Triggers local Apple Silicon MLX LoRA fine-tuning when training data exceeds specified thresholds:

```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

DATASET_PATH = Path.home() / ".my_agent" / "dataset" / "train.jsonl"
ADAPTER_PATH = Path.home() / ".my_agent" / "adapters" / "latest"
TRAIN_THRESHOLD = 100

def run_evolution():
    if not DATASET_PATH.exists():
        return

    total_samples = sum(1 for _ in open(DATASET_PATH, "r", encoding="utf-8"))
    if total_samples < TRAIN_THRESHOLD:
        return

    cmd = [
        "python3", "-m", "mlx_lm.lora",
        "--model", "Qwen/Qwen2.5-Coder-7B-Instruct",
        "--data", str(DATASET_PATH.parent),
        "--train", "--iters", "600", "--batch-size", "2",
        "--adapter-path", str(ADAPTER_PATH)
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    run_evolution()

```

---

## 4. Orchestration Schedule (Crontab)

Decoupled execution ensures optimal compute management across tasks:

```bash
# 1. Memory Stage: Runs hourly (Ultra-lightweight, fast sync)
0 * * * * python3 ~/.my_agent/memory.py > /dev/null 2>&1

# 2. Reflection Stage: Runs daily at 2:00 AM (Medium load, LLM data cleaning)
0 2 * * * python3 ~/.my_agent/reflection.py > /dev/null 2>&1

# 3. Evolution Stage: Runs Sundays at 4:00 AM (High load, local MLX LoRA fine-tuning)
0 4 * * 0 python3 ~/.my_agent/evolution.py > ~/.my_agent/evolution.log 2>&1

```

---

## 5. Architectural Advantages

| Feature | HTTP Proxy Scheme | Event Hook Scheme (V1.0) | **V2.2 Local Skill Pipeline** |
| --- | --- | --- | --- |
| **Terminal Overhead** | +50-200ms network delay | +5-10ms sub-process delay | **Zero baseline overhead; subprocess only on recall** |
| **Setup Complexity** | Port binding & proxy config | Custom script hook binding | **Local Skill + Python scripts; no service lifecycle** |
| **Data Integrity** | Payload intercept required | Event payload coverage dependent | **100% Native SQLite store read** |
| **Safety & Concurrency** | Network error handling | Write-lock management | **Read-only SQLite ingestion and read-only recall interface** |
| **State Tracking** | DB migrations | Custom SQLite tables | **Plain-text checkpoints** |