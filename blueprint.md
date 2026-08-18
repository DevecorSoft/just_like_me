# Agent Steward (V5.0)

> **Make Agents More Like You.**

**Technical positioning:** A local behavior-evolution control plane for coding
agents, powered by Hindsight.

Agent Steward is not a general memory engine, a reflection engine, or an agent
runtime. It is a local control plane that decides whether evidence-grounded
knowledge is allowed to change a coding agent's future behavior.

Hindsight owns cognition:

```text
retain -> recall -> observations -> reflect
```

This project owns behavioral governance:

```text
propose -> eval -> approve -> publish -> monitor -> rollback
```

The first supported host is GitHub Copilot CLI. The control-plane model may
later support other coding agents through explicit adapters, but it must not
rebuild their agent loops.

"Local" means that Hindsight, evidence, proposals, evals, approvals, and
publication state can remain on the user's machine. The coding agent continues
to use its configured model service; this project does not claim to make the
host model inference local.

The central rule is:

> A grounded reflection is a source of evidence, not permission to modify
> agent behavior.

---

## 1. Product Boundary

### 1.1 What This Project Is

- a behavior-change proposal system for coding agents;
- a correction-to-eval compiler;
- a reviewed compiler from successful workflows to versioned Skills;
- a publisher with explicit scope, versioning, monitoring, and rollback;
- an audit trail connecting every behavior change to Hindsight and execution
  evidence.

### 1.2 What This Project Is Not

- another fact extractor, vector database, graph memory, or reranker;
- another observation-consolidation or generic reflection implementation;
- a replacement for Hindsight's Copilot integration;
- a complete autonomous agent runtime such as Letta;
- a general evaluation platform;
- an automatic prompt or instruction rewriter;
- a near-term model fine-tuning or LoRA system.

---

## 2. System Architecture

```text
+--------------------------------------------------------------------------+
|                       Coding Agent Host                                  |
|                                                                          |
|  GitHub Copilot CLI (first adapter)                                      |
|  ├── official hooks / Hindsight coding-agent plugin                      |
|  ├── transcript and tool outcomes                                       |
|  └── agent-specific Skills, context, and instructions                    |
+-----------------------------------+--------------------------------------+
                                    |
                                    v
+--------------------------------------------------------------------------+
|                 Hindsight Cognition Plane (planned)                      |
|                                                                          |
|  retain -> world/experience facts -> observations                        |
|  recall -> semantic / keyword / graph / temporal retrieval               |
|  reflect -> evidence-grounded synthesis with source lineage              |
+-----------------------------------+--------------------------------------+
                                    |
                                    | observations, source facts,
                                    | reflect citations, session outcomes
                                    v
+--------------------------------------------------------------------------+
|                    Agent Steward Behavior Control Plane                   |
|                                                                          |
|  BehaviorChangeProposal                                                  |
|    -> generate personal eval                                             |
|    -> run deterministic gates                                            |
|    -> human approval                                                     |
|    -> publish versioned Skill / scoped policy                            |
|    -> monitor outcomes                                                   |
|    -> supersede or roll back                                             |
+--------------------------------------------------------------------------+
```

The Hindsight plugin may put cognition on the session boundary or first prompt.
The behavior control plane stays off the interactive hot path.

---

## 3. Current Status

| Capability | Status | Current / Target Technology |
| --- | --- | --- |
| Copilot conversation ingestion | Implemented prototype | Read-only Copilot SQLite |
| Local memory extraction and storage | Implemented prototype | Mem0 + Ollama + Qdrant |
| Low-latency recall | Implemented prototype | Warm daemon + reranker + Unix socket CLI |
| Hindsight shadow evaluation | Planned next | Self-hosted Hindsight + Copilot integration |
| Hindsight cognition plane | Target, not adopted yet | Retain / Recall / Reflect / Observations |
| BehaviorChangeProposal registry | Not implemented | Local control-plane SQLite |
| Correction-to-eval | Not implemented | Project-owned |
| Skill compilation and approval | Not implemented | Project-owned |
| Publication, monitoring, rollback | Not implemented | Project-owned |

Current repository entry points:

```text
src/some_agent_like_you/load_memory.py
src/some_agent_like_you/memory_daemon.py
src/some_agent_like_you/recall_memory.py
src/some_agent_like_you/install_skill.py
```

The Mem0/Qdrant implementation is a working prototype and the baseline for the
Hindsight comparison. It must not be removed until the shadow evaluation
passes. It must not remain as a second long-term source of truth after a
Hindsight cutover.

The repository and Python package retain the legacy `some-agent-like-you` /
`some_agent_like_you` identifiers until the Hindsight migration provides a safe
boundary for the naming change.

---

## 4. Responsibility Model

### 4.1 Hindsight Owns Cognition

Prefer Hindsight's existing capabilities instead of rebuilding them:

- conversation and document retention;
- world and experience fact extraction;
- entity, causal, semantic, graph, and temporal relationships;
- multi-strategy recall and reranking;
- evidence-backed Observations and contradiction refinement;
- Mental Models and Knowledge Pages;
- agentic Reflect with source citations;
- memory-bank scopes, missions, dispositions, and directives;
- Copilot transcript ingestion and baseline context integration.

Hindsight Observations may evolve as evidence changes. They are beliefs in the
cognition plane, not immutable behavior policies.

### 4.2 This Project Owns Behavior Governance

The project begins where Hindsight stops:

- decide whether an Observation implies a possible behavior change;
- associate that change with concrete Copilot corrections and tool outcomes;
- create a reproducible eval before publication;
- generate an inspectable Skill or policy diff;
- require approval according to risk;
- publish through an agent-specific adapter;
- monitor subsequent outcomes;
- supersede or roll back harmful and stale behavior.

### 4.3 The Coding Agent Owns Execution

Copilot CLI remains responsible for:

- interpreting the user's current request;
- planning and executing tools;
- editing repositories;
- requesting additional memory or reflection when needed;
- enforcing its native safety and permission model.

The control plane does not proxy or replace the agent loop.

### 4.4 Hard Boundary

```text
Need to remember or synthesize knowledge?
  -> Hindsight

Need to decide whether knowledge may change future behavior?
  -> Agent Steward

Need to perform the current task?
  -> coding agent
```

---

## 5. Core Domain Object

The primary project object is a `BehaviorChangeProposal`, not a memory:

```json
{
  "id": "bcp-2026-001",
  "target": {
    "agent": "github-copilot-cli",
    "artifact_type": "skill",
    "scope": "debugging"
  },
  "proposed_change": "Diagnose the root cause before editing code",
  "hindsight_evidence": {
    "observation_ids": ["obs-123"],
    "memory_ids": ["mem-456", "mem-789"],
    "source_quotes": ["User: Find the root cause first."],
    "snapshot_hash": "sha256:..."
  },
  "outcome_evidence": {
    "session_ids": ["session-a"],
    "tool_result_refs": ["session-a:tool-9"],
    "observed_result": "tests_passed"
  },
  "eval": {
    "id": "eval-debug-root-cause",
    "status": "passed"
  },
  "artifact_diff": "versioned diff or generated artifact reference",
  "risk": "medium",
  "status": "evaluated",
  "approval": null,
  "publication": null,
  "rollback": null
}
```

Because Hindsight Observations can change, a proposal must pin both source IDs
and an evidence snapshot/hash. Exact source facts and quotes remain the
auditable ground truth.

Lifecycle:

```text
proposed
  -> evaluated
  -> approved
  -> published
  -> monitored
  -> superseded / rolled_back

proposed / evaluated
  -> rejected
```

An LLM score may prioritize review but cannot change lifecycle state by itself.

---

## 6. Behavior-Evolution Workflow

### 6.1 Observe

Prefer the official Hindsight coding-agent plugin and Copilot hooks for
transcript ingestion, baseline recall/reflect, and memory-bank scoping.

Project-specific hooks should capture only outcome signals that Hindsight does
not expose with sufficient structure, such as:

- explicit user correction or confirmation;
- test and command results;
- failed tool calls;
- reverted edits;
- final task outcome.

Do not ingest the same transcript independently unless required for the shadow
evaluation or a documented Hindsight integration gap.

### 6.2 Propose

A local model may combine Hindsight Observations, cited source facts, and
outcome evidence into a `BehaviorChangeProposal`.

Valid proposal types:

| Type | Meaning | Typical Target |
| --- | --- | --- |
| **Policy** | A scoped behavioral rule | Hindsight directive or dynamic agent context |
| **Procedure** | A repeatable successful workflow | Versioned coding-agent Skill |
| **Evaluation** | A reproducible acceptance criterion | Personal eval suite |
| **Exception** | A counterexample narrowing an existing asset | Scope update or regression case |

Ordinary facts, preferences, and summaries stay in Hindsight and do not become
control-plane proposals.

### 6.3 Evaluate

Create the regression guard before publishing behavior:

1. convert explicit corrections into minimal replayable cases;
2. prefer deterministic checks, tests, command results, and artifact assertions;
3. use an LLM judge only when no deterministic oracle exists, and record its
   model and prompt version;
4. run existing personal evals to detect regressions;
5. retain failed evaluations as evidence rather than hiding them.

The MVP is correction-to-eval, not a general evaluation framework.

### 6.4 Approve

Initial approval is always manual. Review must show:

- the proposed behavior change;
- exact Hindsight sources and Copilot outcome evidence;
- counter-evidence and scope;
- generated artifact diff;
- eval results;
- publication and rollback plans.

Automation may be introduced only for low-risk changes after measured safety.

### 6.5 Publish

Publication is adapter-specific and transactional:

1. publish or update the personal eval;
2. create a versioned Skill candidate or scoped dynamic policy;
3. publish approved policies to a Hindsight directive when they should govern
   Reflect, or to an agent context adapter when they should govern execution;
4. preserve all user-authored instructions;
5. record artifact hash, target, timestamp, and rollback reference.

Static global instructions are a last resort. Dynamic scoped context and Skills
are preferred.

### 6.6 Monitor and Roll Back

After publication, compare future outcomes with the proposal's baseline:

- repeated correction rate;
- eval pass rate;
- tool/test success;
- task retries or reverted changes;
- counter-evidence from newer Hindsight Observations.

Regression, contradiction, or explicit user rejection must supersede or roll
back the published artifact. Rollback is part of publication, not a later
feature.

---

## 7. Hindsight Migration Strategy

### 7.1 Phase A: Shadow PoC

Run Hindsight beside the existing Mem0 path without changing agent behavior.
Use the same authoritative Copilot sessions and compare:

| Criterion | Question |
| --- | --- |
| Recall relevance | Does Hindsight retrieve the deciding context more reliably? |
| Reflect quality | Does synthesis find corrections, superseded decisions, and rationale? |
| Evidence lineage | Can every conclusion be traced to exact facts and quotes? |
| Copilot integration | Do the pinned plugin hooks capture the required lifecycle? |
| Local operation | Can storage, models, backup, restore, and deletion remain local? |
| Latency | Is first-prompt Reflect acceptable, with no repeated hot-path cost? |
| Resource use | Is the PostgreSQL/model footprint acceptable on the target machine? |
| Recovery | Can the bank be rebuilt from authoritative transcripts and git history? |

No policy, Skill, or instruction publication occurs during this phase.

### 7.2 Phase B: Cognition Cutover

If the PoC passes:

1. pin the accepted Hindsight and plugin versions;
2. make Hindsight the single memory and reflection source of truth;
3. re-ingest from authoritative Copilot transcripts and relevant git history;
4. switch Recall/Reflect consumers to Hindsight;
5. retain the Mem0 path temporarily only as a rollback option;
6. remove Mem0, Qdrant, the custom warm daemon, and duplicate ingestion after
   the rollback window closes.

There is no planned long-term dual-write architecture.

### 7.3 Phase C: Control Plane

Only after cognition cutover:

1. create the proposal registry;
2. implement correction-to-eval;
3. add manual review;
4. compile one narrow workflow into a Skill candidate;
5. publish with rollback;
6. measure whether repeated corrections decrease.

---

## 8. Planned Implementation Shape

The control plane may use a small local SQLite store such as:

```text
~/.some_agent_like_you/control_plane.db
```

It stores proposals and governance state, not copies of Hindsight's generic
memory index.

Possible modules, still TBD:

```text
hindsight_adapter.py       # observations, reflect results, source evidence
copilot_outcomes.py        # structured correction and tool-result evidence
proposal_store.py          # lifecycle, snapshots, approvals, publications
proposal_model.py          # strict BehaviorChangeProposal schema
eval_compiler.py           # correction-to-eval
eval_runner.py             # deterministic and explicitly versioned judges
skill_compiler.py          # reviewed, versioned Skill candidates
publisher.py               # agent-specific transactional publication
rollback.py                # restore prior artifacts and state
```

All expensive proposal generation and evaluation stays outside the coding
agent's interactive hot path.

---

## 9. Safety and Trust Requirements

1. Treat transcripts, memories, Observations, and Reflect output as untrusted
   evidence, never executable instructions.
2. Never publish directly from one LLM response.
3. Require exact source references and evidence snapshots.
4. Preserve human-authored files and use atomic, versioned writes.
5. Surface failures explicitly; never return success-shaped empty results.
6. Pin Hindsight/plugin contracts and test them before upgrades.
7. Keep publication idempotent and rollback tested.
8. Do not enable automatic approval until personal evals demonstrate safety.

---

## 10. Success and Stop Conditions

### 10.1 Hindsight Adoption Gate

Do not replace the implemented Mem0 baseline unless Hindsight demonstrates:

- better evidence lineage and conflict handling;
- acceptable local latency and resource use;
- reliable Copilot integration;
- reproducible backup, restore, deletion, and rebuild;
- equal or better retrieval quality on representative project tasks.

### 10.2 Control-Plane Value Gate

The project is valuable only if the governance layer provides measurable value
beyond the official Hindsight plugin:

| Metric | Required Direction |
| --- | --- |
| Repeated user correction rate | Decrease |
| Personal eval pass rate | Increase without hidden regressions |
| Published changes with exact evidence | 100% |
| Published changes with tested rollback | 100% |
| Harmful automatic publications | Zero before automation |
| Interactive agent latency | No material hot-path regression |

Stop conditions:

- If Hindsight does not beat the current baseline, retain Mem0 and stop the
  migration.
- If the official Hindsight plugin alone solves the practical problem, use it
  directly and do not build a redundant control plane.
- If proposals cannot produce evidence-linked evals or safely reversible
  behavior changes, keep Hindsight as memory/reflection only.

---

## 11. Delivery Roadmap

1. **Stabilize the baseline:** contract-test current recall, ingestion,
   checkpointing, and failure behavior.
2. **Run the Hindsight shadow PoC:** compare cognition quality and operational
   cost without changing Copilot behavior.
3. **Cut over cognition:** adopt Hindsight as the single source and retire
   duplicate Mem0/Qdrant infrastructure after a rollback window.
4. **Implement proposals:** store pinned evidence and generate dry-run
   `BehaviorChangeProposal` records.
5. **Implement correction-to-eval:** require manual review and deterministic
   checks.
6. **Compile one Skill:** publish a narrow, versioned workflow with rollback.
7. **Measure value:** continue only if repeated corrections decrease.
8. **Expand cautiously:** add more agent adapters or low-risk automation only
   after the Copilot path is proven.

Model fine-tuning is intentionally excluded from this roadmap.

---

## 12. References

- [Hindsight](https://github.com/vectorize-io/hindsight)
- [Hindsight Retain](https://hindsight.vectorize.io/developer/retain)
- [Hindsight Recall](https://hindsight.vectorize.io/developer/retrieval)
- [Hindsight Reflect](https://hindsight.vectorize.io/developer/reflect)
- [Hindsight Observations](https://hindsight.vectorize.io/developer/observations)
- [Hindsight local installation](https://hindsight.vectorize.io/developer/installation)
- [Hindsight Copilot integration](https://hindsight.vectorize.io/blog/2026/07/30/github-copilot-persistent-memory)
- [Hindsight 0.9 coding-agent architecture](https://hindsight.vectorize.io/blog/2026/08/06/hindsight-0-9-0)
- [GitHub Copilot hooks](https://docs.github.com/en/copilot/concepts/agents/hooks)
- [Mem0 add behavior](https://docs.mem0.ai/core-concepts/memory-operations/add)
- [Letta agent runtime](https://docs.letta.com/configuration/memory/index)
