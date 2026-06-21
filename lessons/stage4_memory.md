# Stage 4 — Memory (mostly shared — skim, except L18)

> Tags: 🟢 read fast · 🟡 note the delta. Codex and Claude Code solve "the context window is
> small but sessions are long" almost identically. The only real divergence is how
> formalized persistence is (L18).

---

## L16 — Context manager & history 🟢
**Motto: *The history you send is a curated view, not the raw log.***

**Where to look:** `core/src/context_manager/` (`history.rs`, `normalize.rs`, `updates.rs`), `core/src/context/`, `session/token_budget.rs`, `message-history/`, `handlers/get_context_remaining.rs`.

**The mechanism.** Two histories: the **rollout** (full faithful record, L18) and the
**model-visible context** (normalized, token-budgeted projection rebuilt each turn). The
model can query remaining budget via a tool.

**🟢 vs Claude Code.** Same separation CC makes between its transcript and the budgeted
prompt context. **Don't dwell.**

**The aha.** Separate the *system of record* from the *model-visible projection* of it.

---

## L17 — Compaction 🟢
**Motto: *When you run out of room, summarize the past instead of dropping it.***

**Where to look:** `core/src/compact.rs`, `compact_remote.rs`, `compact_remote_v2.rs`, `tasks/compact.rs`, `session/turn.rs` (`run_inline_auto_compact_task`), `protocol/src/compacted_item.rs`.

**The mechanism.** When the budget tightens, Codex runs a compaction task: summarize the
conversation, replace bulky history with summary + recent turns. It runs **inline** (local
turn) or **remote** (server-side), and triggers automatically mid-turn. The compacted item is
a first-class protocol object that survives in the rollout.

**🟡 vs Claude Code.** Same idea as CC's auto-compact and `/compact`. The small **twist**:
Codex has a **remote** compaction path (server-side, leaning on the Responses API's
server-held state from L03) in addition to the inline one — a consequence of its model API,
not a different philosophy. Otherwise, don't dwell.

**The aha.** A context window is a cache; compaction is summarize-then-evict.

---

## L18 — Rollout & replayable sessions 🟡
**Motto: *Append every event to disk so any session can be replayed or resumed.***

**Where to look:** `rollout/`, `rollout-trace/`, `core/src/rollout.rs`, `session/rollout_reconstruction.rs`, `thread-store/`, `core/src/rollout_budget.rs`.

**The mechanism.** Every turn's items are appended to a **rollout** — a durable, ordered log
(the persisted EQ stream from L01). From it Codex *reconstructs* a thread: resume after a
crash, fork, or replay for debugging. Because protocol items are serializable, persistence is
mostly "write the stream to disk."

**🟡 vs Claude Code.** CC also persists sessions and supports `--resume`/`--continue`, so
resume itself is shared. The **delta**: Codex models this as explicit, structured
**event-sourcing** (a dedicated `rollout` crate + `rollout-trace` + reconstruction), which is
why fork/replay/trace fall out cleanly. CC's transcript persistence is more file-oriented.
Worth a skim to see event-sourcing done deliberately.

**The aha.** An append-only event log gives you crash recovery, resume, fork, audit, and
time-travel debugging for the price of serializing a stream you already had.

---

## L19 — AGENTS.md, skills & memories 🟢
**Motto: *Persist instructions, not just facts — and match the store to the lifetime.***

**Where to look:** `core/src/agents_md.rs` (+ `docs/agents_md.md`), the repo's own `AGENTS.md`, `core-skills/` + `core/src/skills.rs` (+ `docs/skills.md`), `memories/` + `protocol/src/memory_citation.rs`.

**The mechanism.** Three durable-knowledge layers: **AGENTS.md** (project instructions
injected into the prompt), **skills** (packaged capabilities loaded on demand, paired with
`tool_search`), **memories** (durable facts the agent stores and later *cites*).

**🟢 vs Claude Code.** Near-direct mapping: **`AGENTS.md` ≈ `CLAUDE.md`**, Codex skills ≈ CC
skills, memories ≈ CC's memory. **Don't dwell** — the filename differs, the mechanism doesn't.
(Notably, `AGENTS.md` is becoming a cross-tool convention, so this is convergence, not
divergence.)

**The aha.** Durable knowledge has three lifetimes — per-project, per-capability, per-fact —
each deserving its own store and injection path.
