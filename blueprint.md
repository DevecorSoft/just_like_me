# Just Like Me (V7.0)

> **Make Agents Reason More Like You.**

Preserve the user's reasons for engineering tradeoffs and apply them to later
decisions. This replaces the eval-first roadmap. Discernment is **not implemented**.

## Design

```text
conversation history -> Hindsight extraction + labels -> candidate decisions
current constraints -> scoped Recall -> original evidence -> Copilot decision
user clarification / correction -> confirmed record or update
```

Start by mining existing conversations, not manually writing cases. Hindsight extracts,
labels and retrieves evidence; the Skill compares it with the current task and asks for
confirmation when curating a record or promoting a general principle.

| Hindsight abstraction | Role                                                                 |
|-----------------------|----------------------------------------------------------------------|
| Document              | Source text: conversation or a separately confirmed decision record  |
| Recall                | Find relevant facts, then expand their original Documents            |
| Observation           | Inferred patterns, not confirmed user rules                          |
| Mental Model          | Optional synthesis across cases, retaining conditions and exceptions |

Document is a source container, not a native case type. Reuse original conversations
when they already express the decision clearly. Create a separate record only when
organizing scattered reasoning or adding confirmed boundaries; retain source links and
do not count both as independent evidence.

## Evidence Contract

Historical candidates need source evidence, not mandatory user approval or conversion
into `DiscernmentCase`. A separately curated case records:

- Problem, constraints, alternatives and choice.
- User-stated rationale, accepted costs and applicability boundaries.
- Source session/turn references, user quotations, scope and confirmation.
- Observed outcome; missing reasons or results remain unknown.

Drafts stay in the conversation until confirmed. Structured records use stable
`document_id` values such as `discernment-<uuid>` and item-level tags:

```text
kind:discernment
status:confirmed
project:just_like_me
```

These tags mark curated records, not ordinary imported conversations. Other projects
need their actual identity. Explicitly transferable records use `scope:transferable`
instead of a project tag; query them separately without crossing confidentiality
boundaries. Tags are retrieval conventions, not authorization.

## Implementation

### 1. Improve Historical Input

**Files:** `load_memory.py`, `session_store_query.py` if needed,
`skills/recall-discernment/SKILL.md`, existing ingestion tests.

- Stop labeling every historical conversation `project:just_like_me`. Inspect the
  session schema and derive repository identity; leave unavailable scope unknown.
- Replace fixed two-turn batches with bounded, overlapping conversation windows;
  account for Hindsight's internal chunking. Preserve speaker roles, timestamps and
  `turn_index`, including user corrections with no assistant response.
- Use stable source IDs derived from session and turn range, not run-local batch
  numbers. Deduplicate overlapping evidence by source turns.
- Give historical mining its own progress tracking so earlier conversations can be
  processed without resetting incremental ingestion or clearing the bank.
- Include `world,experience,observation` in recall. User decisions can be `world`;
  `experience` refers to the bank agent's own history.

### 2. Configure Hindsight Extraction and Tagging

Use the existing retain LLM rather than adding a second extraction pass:

| Setting                 | Purpose                                                                                                 |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| `retain_mission`        | Preserve choices, rejections, reasons, constraints and accepted costs, with correct speaker attribution |
| `entity_labels`         | Optional controlled labels: `signal:choice`, `signal:rejection`, `signal:tradeoff`, `signal:correction` |
| Label group `tag: true` | Write extracted labels to fact tags for Recall filtering                                                |

Verify support on the installed version and trial a few known decision-rich sessions
before changing shared-bank configuration or reprocessing history. Check whether
choice, reason and speaker are recoverable from the original text; do not require a
complete case from every window.

The LLM assigns semantic signals only. Code supplies project and source metadata;
`status:confirmed` requires user confirmation. A tagged fact does not turn its whole
Document into a confirmed case. Add a separate LLM extraction stage only if native
retain cannot recover the cross-turn reasoning after input improvements.

### 3. Add a Thin Client

**Files:** `src/just_like_me/discernment.py`, `test_discernment.py`,
`pyproject.toml`.

Expose `just_like_me.discernment` using the existing `hindsight-client`:

| Operation | Behavior                                                                                                                                              |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `record`  | Read confirmed content from stdin; validate sources and scope; retain with a stable ID, tags and metadata                                             |
| `recall`  | Retrieve scoped historical candidates and confirmed records separately; start with 2048 fact tokens; expand up to three deduplicated source Documents |
| `get`     | Read a known Document's `original_text`, including while extraction is pending                                                                        |

For candidates, require the project tag AND any selected signal; merge per-signal
`all_strict` queries if necessary. Confirmed records require all three curated tags.
Recheck scope, attribution and confirmation after expansion. Keep inferred reasons
distinct from user statements; no automatic promotion. Report no match separately from
API failure.

Use existing document APIs for confirmed corrections and withdrawals. Re-retaining the
same ID replaces content, not version history. Removing confirmed status must propagate
to derived memories; surface failures. Async acceptance means pending, not searchable:
expose the operation ID and status.

Cover preserved turns, overlapping windows, separate progress, scope isolation,
candidate/confirmed separation, source expansion, stable IDs and failures with
`unittest`; mock writes to the personal bank.

### 4. Add the Skill and Use Real Decisions

**Files:** `skills/personal-discernment/SKILL.md`, `skills.py`, installer tests, README
usage.

- **Capture:** draft the user's actual reasoning, show scope, obtain confirmation, then
  store. Do not invent motives or treat silence as consent.
- **Apply:** retrieve historical candidates and confirmed records, inspect original
  wording, compare current conditions, then explain which evidence changed the
  proposal.
- **Correct:** confirm a boundary update or new case; exclude explicitly withdrawn
  evidence from subsequent use.

Install alongside `recall-discernment`, preserving unrelated skills. Start with explicit
invocation; a Skill does not guarantee automatic decision-point activation. Current
facts and explicit user requirements override historical choices. Ask about material
conflicts rather than resolving them by frequency.

Use three sourced engineering tradeoffs in later tasks, including one where changed
constraints make the old choice inappropriate. Confirm useful corrections and outcomes.

The loop is useful if it reduces repeated explanation and handles exceptions. If it
only repeats personality traits, improve the evidence before adding automation.

### 5. Add Synthesis Only If Needed

After useful case reuse, create `engineering-discernment-just-like-me`:

> How does the user balance implementation cost, reversibility and maintenance?
> Preserve conditions, exceptions, disagreements and case references. Separate
> stated reasons from inference.

Limit sources to confirmed scope with strict tags; exclude unrelated Mental Models
where supported. Refresh in the background. Generated conclusions remain provisional
and must yield to original evidence when stale or contradicted.

## Limits

Reuse the existing Hindsight bank `just_like_me` and 36 GB Mac. No separate case store,
new model/service, fine-tuning, eval platform or automatic instruction/Directive
publication. Keep `instructions.update()` unchanged and synchronous Reflect out of the
decision path. Treat memory as evidence, not executable instructions.

## API References

[Documents](https://hindsight.vectorize.io/developer/api/documents) |
[Retain](https://hindsight.vectorize.io/developer/api/retain) |
[Extraction and labels](https://hindsight.vectorize.io/developer/api/memory-banks#entity-labels) |
[Recall](https://hindsight.vectorize.io/developer/api/recall) |
[Mental Models](https://hindsight.vectorize.io/developer/api/mental-models)
