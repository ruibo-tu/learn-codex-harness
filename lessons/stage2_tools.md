# Stage 2 — Tools (how the model acts)

> Tags: 🔴 focus · 🟡 skim delta · 🟢 read fast. Two big divergences live here: **L07
> apply_patch** and **L08 code mode**.

A tool = **a spec (what the model sees) + a handler (what runs) + a result (what feeds
back)**. Note in `core/src/tools/handlers/` that nearly every tool ships a `*.rs` handler
**and** a `*_spec.rs`.

---

## L05 — The tool registry & router 🟢
**Motto: *Tools are data; dispatch is a table lookup.***

**Where to look:** `core/src/tools/registry.rs`, `router.rs`, `mod.rs`, `handlers/mod.rs`, `tools/` crate (`ToolName`).

**The mechanism.** The registry holds specs; the router dispatches a model tool-call to a
handler. `ToolName` is a typed, namespaced value so builtin / MCP / dynamic tools coexist.
Which tools exist on a turn is dynamic (config, sandbox, MCP, skills).

**🟢 vs Claude Code.** Same pattern as CC's tool table. **Don't dwell** — both keep `match`
out of the loop and register `{spec, handler}` pairs.

**The aha.** Adding a tool must never touch the loop.

---

## L06 — Shell & unified exec 🟡
**Motto: *Every dangerous capability funnels through one audited door.***

**Where to look:** `core/src/tools/handlers/shell/`, `handlers/unified_exec/`, `core/src/exec.rs`, `exec_env.rs`, `spawn.rs`, `command_canonicalization.rs`, `exec-server/`.

**The mechanism.** `unified_exec` is the single path for spawning processes: commands are
**canonicalized** (so `./x`, `x`, absolute paths resolve to one identity for policy),
run with a controlled environment, and **always launched inside the sandbox** (Stage 3).

**🟡 vs Claude Code.** Both funnel commands through one Bash/exec tool, so the *chokepoint*
idea is shared. The **twist** worth noting: Codex's `command_canonicalization` exists
specifically to feed the sandbox/exec-policy decision (L13) — canonicalization is a *safety*
input, not just hygiene. CC's Bash tool leans on permission-rule matching instead.

**The aha.** The chokepoint is where canonicalization, truncation, auditing, *and* the
sandbox entry all converge.

---

## L07 — apply_patch vs Edit/Write 🔴
**Motto: *Edit files through a patch grammar, not string surgery.***

**Where to look:** `apply-patch/` crate (`parser.rs`, `streaming_parser.rs`, `seek_sequence.rs`), `core/src/apply_patch.rs`, `core/src/tools/handlers/apply_patch.rs`, `handlers/apply_patch.lark` (the grammar).

**The mechanism.** Codex defines a small **patch language** — `*** Add/Update/Delete File`
with context hunks — backed by a real grammar (`apply_patch.lark`) and both a batch and a
**streaming** parser. `seek_sequence.rs` locates each hunk's context in the live file so
edits apply even when line numbers drift. The edit is one structured, diffable, approvable
object.

**🔴 vs Claude Code.** This is a genuine philosophical fork in how an LLM edits code:
- **Codex = one patch format.** The model emits *one* `apply_patch` blob describing many
  files/hunks at once. Pros: atomic multi-file change, a single diff to review/approve,
  one grammar to validate, resilience to miscounted line numbers via context-matching.
- **Claude Code = a family of edit tools.** `Edit` (find-and-replace a unique string),
  `Write` (whole file), `MultiEdit` (several edits in one file). Pros: dead simple, no
  grammar; the model just supplies old→new strings. Cons: each edit is its own call, and
  uniqueness/whitespace matching is the failure mode instead of hunk context.
- **Consequence for the harness:** Codex's structured patch is *why* its diff rendering
  (L23) and sandboxed file-write checks compose so cleanly — the change is a first-class
  object before it touches disk. CC's string edits are validated more at apply time.

**The aha.** If your agent edits code, choosing the *edit protocol* (patch grammar vs
string replacement) is a top-level design decision — it dictates your review UX, your
failure modes, and how safety inspects changes.

---

## L08 — Code mode: calling tools by writing code 🔴
**Motto: *Sometimes the best tool call is a program that makes many tool calls.***

**Where to look:** `code-mode/` (`service.rs`, `runtime/`, `cell_actor/`), `code-mode-protocol/` (`render_json_schema_to_typescript`, `build_exec_tool_description`, `CodeModeNestedToolCall`, `ExecuteRequest`/`WaitRequest`), `code-mode-host/`.

**The mechanism.** In **code mode**, tools are presented to the model as a **TypeScript
API** (their JSON schemas are rendered to TS types via `render_json_schema_to_typescript`),
and the model responds by *writing code* that calls those functions. Codex runs that code in
a runtime where each call becomes a **nested tool call** (`CodeModeNestedToolCall`), with
`exec`/`wait` semantics and per-call output-token budgets. One model turn can thus orchestrate
a whole sequence of tool calls *in code* — loops, conditionals, intermediate variables —
instead of emitting them one JSON call at a time.

**🔴 vs Claude Code.** No CC equivalent. CC is **pure JSON function-calling**: the model
emits one structured tool call, gets a result, emits the next. Code mode trades that for
expressiveness (the model programs its tool use) at the cost of a sandboxed code runtime and
a more complex protocol. It's the most distinctive thing in Codex's tool layer.

**The aha.** Tool *invocation* itself is a design space. JSON-per-call is the default
everywhere, but "let the model write code that calls tools" is a real alternative that
collapses multi-step tool sequences into one turn — at the price of needing a runtime you
can sandbox.

---

## L09 — Parallel tool calls & the orchestrator 🟢
**Motto: *Run independent work concurrently; serialize what touches shared state.***

**Where to look:** `core/src/tools/orchestrator.rs`, `parallel.rs`, `lifecycle.rs`, `context.rs` (shared `TurnDiffTracker`).

**The mechanism.** A turn can request several tool calls; the orchestrator runs them with
bounded concurrency, the lifecycle layer emits begin/end events, and a shared diff tracker
merges parallel edits into one coherent diff.

**🟢 vs Claude Code.** CC also runs independent tool calls in parallel and serializes
stateful ones. **Don't dwell.** Same lesson: concurrency is a tool-layer concern kept out of
the loop.

**The aha.** The loop says "run these calls"; the orchestrator decides how.

---

## L10 — The auxiliary tools 🟢
**Motto: *Some "tools" structure the conversation, not the world.***

**Where to look:** `core/src/tools/handlers/plan.rs`, `view_image.rs`, `web_search.rs`, `request_user_input.rs`, `request_permissions.rs`, `get_context_remaining.rs`, `tool_search.rs`, `sleep.rs`.

**The mechanism.** Several handlers don't touch the OS: **plan** (visible task list),
**request_user_input / request_permissions** (pause and ask — emit EQ events), **view_image
/ web_search** (pull context in), **get_context_remaining** (self-introspect budget),
**tool_search** (discover tools on demand).

**🟢 vs Claude Code.** Direct analogues: `plan` ≈ CC's `TodoWrite`; ask-the-user ≈ CC's
permission/question prompts; web/image ≈ CC equivalents. **Don't dwell.** Same insight: the
tool interface is the general extension point, including for human-in-the-loop and
self-inspection.

**The aha.** "Tool" generalizes to any structured interaction — even asking the human or
reasoning about your own limits.
