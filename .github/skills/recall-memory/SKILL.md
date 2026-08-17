---
name: recall-memory
description: Query user memory for prior preferences, decisions, constraints, corrections, and project context. Use always.
---

# Recall user memory

## Usage

```shell
uv run recall-memory --limit 5 "<semantic query>"
```

Stdout is a JSON array of recall items.

- Empty array: continue without recalled context.
- Command failure: report retrieval failure explicitly; do not treat it as empty success.
