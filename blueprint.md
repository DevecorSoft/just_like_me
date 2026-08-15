# Ultra-Lightweight Self-Evolving Architecture Scheme for Personal AI Agent (Digital Twin)

This scheme is built upon **GitHub Copilot CLI native extension mechanisms**, the **Mem0 dynamic memory engine**, and a
**zero-dependency offline evolution daemon**. It eliminates the need for black-box HTTP proxies and Web services
(such as FastAPI), achieving zero background process footprint, zero terminal latency overhead, fact-level memory
overwrite, and long-term self-evolution.

---

## 1. Overall Architecture

The architecture is divided into the **Frontend Native Sensing Layer**, **Explicit Memory Layer**, and **Offline
Evolution Brain**:

```
+-------------------------------------------------------------------------+
|                Frontend: Copilot CLI (Native Terminal Host)             |
|                                                                         |
|  ├── Static Rules : ~/.copilot-instructions.md  (Rewritten by Daemon)    |
|  ├── Event Hooks  : ~/.copilot/hooks.json       (Triggers script logging)|
|  └── Memory IF    : ~/.copilot/mcp.json         (Mounts Mem0 MCP server)  |
+-----------------------------------+-------------------------------------+
                                    | Triggers stdio pipeline
                                    v
+-------------------------------------------------------------------------+
|             Backend: Offline Evolution Daemon (Cron / Async Task)       |
|                                                                         |
|  ├── 1. Zero-dep logging  : log_collector.py saves stdin to raw_logs    |
|  ├── 2. Data extraction   : Extracts user edits into "Golden Pair" JSONL|
|  ├── 3. Meta-reflection   : Rewrites ~/.copilot-instructions.md         |
|  ├── 4. Explicit memory   : Resolves conflicts & CRUD via Mem0 API      |
|  └── 5. Weight evolution  : Triggers light MLX LoRA fine-tuning         |
+-------------------------------------------------------------------------+

```

---

## 2. Core Technology Selection

| Module                       | Technology                     | Core Responsibilities                                                                                                     |
|------------------------------|--------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Interactive Host**         | GitHub Copilot CLI             | Native terminal Shell interaction, code completion, and Agent tool calling                                                |
| **Fact Memory Engine**       | Mem0 (`@mem0/mcp`)             | Explicit fact extraction, tri-level scope isolation (User/Session/Agent), and memory conflict resolution (CRUD)           |
| **Rules & Habits Layer**     | `~/.copilot-instructions.md`   | Native static Context mounting, zero extra inference latency, defines code style and mandatory constraints                |
| **Log Capture Endpoint**     | Native Python 3 Script (Stdio) | Runs for ~10ms only when triggered by events, zero third-party dependencies, captures JSON data automatically via `stdin` |
| **Offline Evolution Engine** | Python Scheduled Task (Daemon) | Data cleaning, Golden Pair extraction, meta-reflection, and automatic Prompt/LoRA evolution                               |
| **Local Weight Fine-Tuning** | MLX LoRA (Apple Silicon)       | Consumes high-value JSONL datasets to update base model tone and coding habits                                            |

---

## 3. Configuration & Core Code Implementation

### 3.1 Configure Mem0 MCP Service

Register the official Mem0 memory interface in `~/.copilot/mcp.json`:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "npx",
      "args": [
        "-y",
        "@mem0/mcp"
      ],
      "env": {
        "MEM0_API_KEY": "your_mem0_api_key"
      }
    }
  }
}

```

### 3.2 Configure Native Command Mode Hooks

Configure command-line event callbacks in `~/.copilot/hooks.json`, leveraging subprocess pipes for data transfer:

```json
{
  "hooks": {
    "sessionEnd": [
      {
        "type": "command",
        "command": "python3 ~/.my_agent/log_collector.py"
      }
    ]
  }
}

```

### 3.3 Zero-Dependency Log Collector (`~/.my_agent/log_collector.py`)

No Web server required; executes via standard input and exits immediately upon completion:

```python
#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from datetime import datetime


def main():
    # 1. Read Hook JSON data from standard input (stdin)
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return

    try:
        data = json.loads(raw_input)
    except json.JSONDecodeError:
        return

    # 2. Save to ~/.my_agent/raw_logs directory
    log_dir = Path.home() / ".my_agent" / "raw_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = data.get("session_id", timestamp)
    log_file = log_dir / f"session_{session_id}.json"

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

```

---

## 4. Offline Evolution Daemon & JSONL Dataset Accumulation

The offline evolution engine (`~/.my_agent/evolution_daemon.py`) runs asynchronously via cron (e.g., nightly) to perform
**dataset filtering** and **rule evolution**.

```python
#!/usr/bin/env python3
import os
import json
import glob
from pathlib import Path

DATASET_PATH = Path.home() / ".my_agent" / "dataset" / "train.jsonl"
INSTRUCTIONS_PATH = Path.home() / ".copilot-instructions.md"
RAW_LOGS_DIR = Path.home() / ".my_agent" / "raw_logs"

DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)


def extract_golden_pairs(raw_session_data):
    """
    Extract high-quality training pairs from raw session:
    1. Extract user corrections to AI-generated code (error-correction samples)
    2. Extract successfully executed code generation contexts without errors
    """
    golden_pairs = []
    messages = raw_session_data.get("messages", [])

    for i in range(len(messages) - 1):
        if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
            user_input = messages[i]["content"]
            assistant_resp = messages[i + 1]["content"]

            # Filter short text and invalid interactions
            if len(user_input) > 10 and "```" in assistant_resp:
                golden_pairs.append({
                    "messages": [
                        {"role": "system",
                         "content": "You are the user's digital twin, strictly adhering to the user's coding habits and architectural preferences."},
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": assistant_resp}
                    ]
                })
    return golden_pairs


def run_evolution_pipeline():
    log_files = glob.glob(str(RAW_LOGS_DIR / "*.json"))
    new_pairs = []

    for file_path in log_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                new_pairs.extend(extract_golden_pairs(data))
            except json.JSONDecodeError:
                pass
        os.remove(file_path)  # Clean up processed raw logs

    # Append to train.jsonl
    if new_pairs:
        with open(DATASET_PATH, "a", encoding="utf-8") as f:
            for pair in new_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    # Rule evolution: abstract new common preferences to rewrite copilot-instructions.md
    update_instructions_from_patterns()


def update_instructions_from_patterns():
    # Call a lightweight local LLM (e.g., Ollama/Qwen) to analyze the latest train.jsonl
    # Summarize rules such as "Prohibit hardcoded API URLs" and update ~/.copilot-instructions.md
    pass


if __name__ == "__main__":
    run_evolution_pipeline()

```

---

## 5. Local MLX LoRA Offline Fine-Tuning

When "Golden Pairs" in `~/.my_agent/dataset/train.jsonl` reach a predefined threshold (e.g., 100+ entries), the Daemon
automatically triggers local Apple Silicon incremental training:

```bash
# Trigger MLX offline fine-tuning to update habits and style
python -m mlx_lm.lora \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --data ~/.my_agent/dataset \
  --train \
  --iters 600 \
  --batch-size 2 \
  --adapter-path ~/.my_agent/adapters/latest

```

---

## 6. Scheme Comparison & Advantages

| Dimension             | HTTP Proxy Scheme (FastAPI)                             | Current Scheme (Native Command Hook + Offline Evolution)                                                     |
|-----------------------|---------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| **Ports & Processes** | Requires常驻 background Web service occupying port 8000 | **Zero background processes, zero port footprint**; script exits immediately after execution                 |
| **Dependencies**      | Requires `fastapi` / `uvicorn` / `asyncio`              | **Zero third-party dependencies**, runs purely on Python standard library                                    |
| **TTFT / Latency**    | Adds network request and relay unpacking overhead       | **0 extra latency**, static Prompt + Stdio pipeline with zero friction                                       |
| **Fact Memory**       | Self-built vector DB & triples, prone to contradictions | **Managed by Mem0**, native MCP handles CRUD automatically                                                   |
| **Self-Evolution**    | Forcibly rewrites JSON Payload                          | **Background scheduled extraction of Golden Pairs $\rightarrow$ Dynamically rewrites Prompt / Evolves LoRA** |