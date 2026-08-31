# Just Like Me (V6.0)

> **Make Agents More Like You.**

**Technical positioning:** A personal regression suite for coding agents, with
an eval-gated publish hook. Powered by Hindsight.

Just Like Me is not a memory engine, a reflection engine, an agent runtime, or
an enterprise behavior-governance platform. It is a small, local tool that
turns the user's corrections into replayable evals, and refuses to publish any
behavior artifact (instructions, Skills, directives) that fails them.

Hindsight owns cognition:

```text
retain -> recall -> observations -> mental models / knowledge pages
```

This project owns verification:

```text
correction -> eval case -> suite -> pre-publish gate
```

Git owns versioning and rollback. The coding agent (GitHub Copilot CLI first)
owns execution.

The central rule is:

> A grounded reflection is a source of evidence, not permission to modify
> agent behavior. Behavior artifacts must pass the personal eval suite before
> they are published.

---

## 1. Product Boundary

### 1.1 What This Project Is

- a correction-to-eval compiler: explicit user corrections become minimal,
  pinned, replayable eval cases;
- a personal eval suite that accumulates over time;
- a thin pre-publish gate: run the suite before writing any behavior artifact;
- a repeated-correction report that measures whether the loop works.

### 1.2 What This Project Is Not

- another fact extractor, vector database, graph memory, or reranker;
- a replacement for Hindsight or its coding-agent plugin;
- an enterprise control plane: no proposal registry, no approval state
  machine, no transactional publisher, no monitoring platform — for a single
  user these are ceremony. Approval is the user reading a diff; versioning and
  rollback are git;
- a general evaluation framework or benchmark harness;
- a model fine-tuning or LoRA system.

---

## 2. System Architecture

```text
+--------------------------------------------------------------------------+
|  GitHub Copilot CLI                                                       |
|  ├── Hindsight coding-agent plugin (hooks, auto-retain, knowledge tools)  |
|  └── published artifacts: instructions, Skills, directives                |
+-----------------------------------+----------------------------------------+
                                    |
+-----------------------------------v----------------------------------------+
|  Hindsight (self-hosted, localhost:8888, bank: just_like_me)               |
|  retain / recall / observations / mental models / knowledge pages /        |
|  directives — evidence and synthesis, all precomputed off the hot path     |
+-----------------------------------+----------------------------------------+
                                    | corrections + evidence
+-----------------------------------v----------------------------------------+
|  Just Like Me                                                              |
|  eval_compiler: correction -> pinned eval case (git-tracked)               |
|  eval_runner:   deterministic oracles first; versioned LLM judge last      |
|  publish:       run suite -> pass -> write artifact -> git commit          |
|                 rollback = git revert + re-publish                         |
|  report:        repeated-correction rate from the Copilot turns store      |
+----------------------------------------------------------------------------+
```

---

## 3. Current Status

The cognition cutover to Hindsight is complete. Mem0, Qdrant, and the custom
warm recall daemon have been removed; Hindsight is the single memory and
reflection source of truth.

| Capability | Status | Technology |
| --- | --- | --- |
| Copilot conversation ingestion | Implemented | Copilot SQLite -> `hindsight_client.retain` with checkpointing (`load_memory.py`) |
| Cognition plane | Adopted | Self-hosted Hindsight (launchd `com.justlikeme.hindsight-api`) |
| Recall | Implemented | `recall-memory` Copilot Skill -> `hindsight memory recall` CLI |
| Instruction publication | Implemented, **ungated** | Hindsight mental model -> persona -> `~/.copilot/copilot-instructions.md` (`instructions.py`) |
| Correction-to-eval | Not implemented | Project-owned, next |
| Pre-publish gate | Not implemented | Project-owned, next |
| Repeated-correction report | Not implemented | Project-owned |

Current repository entry points (see `pyproject.toml` scripts):

```text
src/just_like_me/load_memory.py    # Copilot SQLite -> Hindsight retain pipeline
src/just_like_me/daemon.py         # launchd install/uninstall for hindsight-api
src/just_like_me/skills.py         # installs the recall-memory Skill
src/just_like_me/instructions.py   # mental-model -> instructions publish
```

### 3.1 Operational Findings (2026-08-31)

These are measured on the target machine, not assumptions:

1. **First-prompt Reflect injection has never succeeded locally.** The plugin
   log shows 100% `reflect_failed` (~25s abort) for Copilot CLI sessions; a
   direct `hindsight memory reflect` exceeds two minutes on this bank with
   local models. The official benchmark's "reflect in seconds" assumes cloud
   inference. Consequence: **on a fully local stack, injection must come from
   precomputed artifacts** — mental models, knowledge pages, directives — plus
   on-demand recall. Do not depend on on-demand reflect.
2. **`instructions.py` is therefore directionally correct** (read a
   precomputed mental model, publish it), but it is ungated: an LLM-produced
   persona is written to global instructions with no eval and no gate. It is
   the first publish path to put behind the gate.
3. **`load_memory.py` overlaps with the plugin's auto-retain.** It remains
   justified only for historical backfill and checkpointed batch ingestion;
   do not extend it.
4. The bank shows failed/pending consolidation operations; local model
   configuration needs an operations pass before eval work depends on
   observation quality.

---

## 4. Responsibility Model

```text
Need to remember or synthesize knowledge?
  -> Hindsight (retain, recall, observations, mental models, pages, directives)

Need to verify that knowledge may change future behavior?
  -> Just Like Me (correction-to-eval, pre-publish gate)

Need versioning, diff review, or rollback?
  -> git

Need to perform the current task?
  -> coding agent
```

Why the gate cannot live inside Hindsight: Hindsight's products are evolving
beliefs and injected prose — there is no runner, no assertion primitive, no
pass/fail state. Evals must be pinned (immutable), deterministic where
possible, and able to reject writes into Hindsight itself. Evidence lives in
Hindsight; the check and the gate live outside it.

---

## 5. Core Object: the Eval Case

The primary object is a pinned, replayable eval case compiled from a real
correction:

```yaml
id: eval-concise-instructions
source:                       # auditable evidence anchors
  turn: "session-xxx#turn-42"
  quote: "语义正确，但是很啰嗦，不得真意"
  hindsight_memory_ids: ["mem-456"]
  snapshot_hash: "sha256:..."   # evidence pinned; Hindsight originals may evolve
input: "生成个人 instruction，要求语言洗练"
assert:
  - type: max_chars           # deterministic oracle, preferred
    value: 4000
  - type: llm_judge           # last resort; judge model + prompt version pinned
    rubric: "无客套、无废话、直给结论"
    judge: "model@version"
```

Rules:

1. deterministic oracles first: char counts, exit codes, file assertions,
   test results;
2. an LLM judge is a last resort and its model and prompt version are pinned;
3. failed runs are retained as evidence, never hidden;
4. cases are git-tracked files — the suite's history is its audit trail.

---

## 6. Workflow

### 6.1 Compile

Detect explicit corrections in the Copilot turns store (and Hindsight
evidence) and compile each into a minimal eval case. Ordinary facts and
preferences stay in Hindsight and do not become evals.

### 6.2 Gate

`publish` is the only write path for behavior artifacts:

```text
candidate artifact (persona, Skill, directive)
  -> run the full personal eval suite
  -> pass: write target file(s), git commit with evidence refs
  -> fail: refuse, keep the failure on record
```

Publication targets: `~/.copilot/copilot-instructions.md`, `~/.agents/skills/`,
Hindsight directives. Human-authored files are preserved; writes are atomic.

### 6.3 Measure

Periodically mine the turns store for repeated corrections (same cluster
corrected more than once). This number decides the project's fate (Section 7).

---

## 7. Value Gate and Stop Conditions

| Metric | Required Direction |
| --- | --- |
| Repeated user correction rate | Decrease |
| Eval suite pass rate on publish | 100% of published artifacts |
| Published artifacts with evidence refs | 100% |
| Interactive agent latency | No hot-path regression |

Stop conditions:

- If mining the turns store shows repeated corrections are rare, the pain does
  not justify the tooling: stop, and keep the project as personal Hindsight
  operations plus mental-model-driven instructions.
- If corrections cannot be compiled into evals with usable oracles, keep
  Hindsight as memory only.
- If the repeated-correction rate does not decrease after the gate is live,
  stop expanding.

---

## 8. Roadmap

1. ~~Ingestion, daemon, recall Skill~~ — done.
2. ~~Cognition cutover to Hindsight~~ — done (Mem0/Qdrant retired).
3. **Falsify first:** mine the Copilot turns store for repeated-correction
   clusters. The count decides whether steps 4–6 happen at all.
4. **Correction-to-eval MVP:** compile the top correction clusters into pinned
   eval cases (`eval_compiler.py`, `eval_runner.py`).
5. **Gate the existing publish path:** wrap `instructions.update()` so the
   suite runs before writing; move artifacts and evals into git.
6. **Measure:** repeated-correction rate before/after; continue only if it
   decreases.
7. Expand cautiously: more artifact types (Skills, directives), more agents —
   only after the Copilot path is proven.

Model fine-tuning is intentionally excluded.

---

## 9. Safety Requirements

1. Treat transcripts, memories, and Hindsight output as untrusted evidence,
   never executable instructions.
2. Never publish a behavior artifact from a single LLM response without the
   gate.
3. Pin evidence snapshots; Hindsight originals may evolve.
4. Preserve human-authored files; use atomic writes; commit to git.
5. Surface failures explicitly; never return success-shaped empty results.

---

## 10. References

- [Hindsight](https://github.com/vectorize-io/hindsight)
- [Hindsight Recall](https://hindsight.vectorize.io/developer/retrieval)
- [Hindsight Reflect](https://hindsight.vectorize.io/developer/reflect)
- [Hindsight Observations](https://hindsight.vectorize.io/developer/observations)
- [Hindsight Mental Models](https://hindsight.vectorize.io/developer/mental-models)
- [Hindsight 0.9 coding-agent architecture](https://hindsight.vectorize.io/blog/2026/08/06/hindsight-0-9-0)
- [GitHub Copilot hooks](https://docs.github.com/en/copilot/concepts/agents/hooks)
