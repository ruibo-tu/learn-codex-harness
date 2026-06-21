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

## In this folder

- **`code.py`** — runnable demo (offline, no deps):
  ```bash
  python3 lessons/s08_code_mode/code.py
  ```
- **`images/code_mode.svg`** — diagram for this lesson.
