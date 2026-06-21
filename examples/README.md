# Runnable examples

Tiny, **self-contained** programs that demonstrate Codex's harness mechanisms —
weighted toward the ones that **diverge from Claude Code**. Each maps to a lesson
in [`../lessons/`](../lessons/).

> **Zero setup.** Pure Python 3.8+ standard library — **no dependencies, no API
> key, no network.** The "model" is a deterministic mock so the focus stays on
> the *harness*, not the LLM. (The originals in `learn-claude-code` call the real
> API; these run anywhere, offline.)

```bash
python3 examples/01_sqeq_loop.py
python3 examples/02_apply_patch.py
python3 examples/03_sandbox_first_safety.py
python3 examples/04_code_mode.py
python3 examples/05_tool_registry.py
```

| File | Lesson | Tag | What it shows |
|---|---|---|---|
| `01_sqeq_loop.py` | L01–L02 | 🟡 | The Submission Queue → loop → Event Queue spine; surfaces are just queue readers. |
| `02_apply_patch.py` | L07 | 🔴 | A mini `apply_patch` parser/applier with context-matching, vs string-replace `Edit`. |
| `03_sandbox_first_safety.py` | L11–L15 | 🔴 | The same commands through Codex's *sandbox-first* and CC's *approval-first* decision engines. |
| `04_code_mode.py` | L08 | 🔴 | Tools rendered as a typed API; the model writes a program → many nested tool calls in one turn. |
| `05_tool_registry.py` | L05/L09 | 🟢 | Namespaced tool registry + router + bounded parallel orchestration; adding a tool never touches the loop. |

Legend: 🔴 diverges from Claude Code (focus) · 🟡 twisted · 🟢 same.

These are **teaching reductions**, not Codex's real code — the production logic
lives in Rust under `codex-rs/` (e.g. `apply-patch/`, `sandboxing/`,
`code-mode/`, `core/src/tools/`). Read the example to get the idea, then open the
crate to see it at scale.
