---
marp: true
theme: default
paginate: true
title: Learn Codex as a Harness — the Claude Code diff
---

<!--
This is a Marp deck (https://marp.app). Render it to HTML / PDF / PPTX:
    npx @marp-team/marp-cli@latest slides/codex-harness.md -o slides/codex-harness.html
    npx @marp-team/marp-cli@latest slides/codex-harness.md --pdf
No install needed to read it — it's just Markdown.
-->

# Learn **Codex** as a Harness

### Reading `openai/codex`, weighted by how it differs from Claude Code

*One agent loop stays untouched. Each lesson adds one wrapper. Each wrapper has a motto.*

---

## The one sentence

> **Codex is a Rust binary that runs your commands *inside an OS kernel sandbox
> by default and asks only on escape*. Claude Code is a Node program that *asks
> you before it acts* by default.**

Almost every other difference flows from that — and from the language choice.

*(Codex is open source; Claude Code is closed, so CC claims are architecture-level.)*

---

## The spine — identical in both systems 🟢

```
 user ─▶ Submission Queue ─▶ [ THE LOOP ] ─▶ Event Queue ─▶ surface
                                  │
        tools · sandbox · approvals · context · memory · MCP · surfaces
                  every one is a WRAPPER, never a loop edit
```

So we **skim the loop** and **spend our time on the wrappers that diverge**.

---

## Divergence legend

| Tag | Meaning | Read it |
|----|---------|---------|
| 🔴 | Codex does this **fundamentally differently** | **slow down** |
| 🟡 | same idea, different shape | skim the delta |
| 🟢 | architecturally the same as CC | don't dwell |

---

## The whole map (one slide)

| Dimension | Codex | Claude Code | |
|---|---|---|---|
| Implementation | Rust single binary | TypeScript/Node | 🔴 |
| Default safety | sandbox-first | approval-first | 🔴 |
| OS sandbox | Seatbelt/Landlock/bwrap/Win | lighter/optional | 🔴 |
| File edits | `apply_patch` grammar | `Edit`/`Write` | 🔴 |
| Tool calling | JSON **+ code mode** | JSON only | 🔴 |
| Approval reviewer | human **or guardian AI** | human or hook | 🔴 |
| Model API | Responses + ollama/lmstudio | Messages + Bedrock/Vertex | 🟡 |
| Extra surfaces | **voice, cloud-tasks** | — | 🔴 |
| MCP/hooks/skills/compaction/subagents/`AGENTS.md`≈`CLAUDE.md` | ~same | ~same | 🟢 |

---

## 🔴 #1 — Sandbox-first vs approval-first

- **Codex:** run the command in Seatbelt/Landlock, **network off**; only
  **escalate to a human on a sandbox escape**.
- **Claude Code:** **ask first** (or match allowlist/hook); sandbox is optional.

Consequence: Codex bothers you *less* for safe-but-not-allowlisted work, and
trusts the **kernel** as the safety net instead of the **human**.

`▶ examples/03_sandbox_first_safety.py` · `▶ diagrams/01_safety_decision.svg`

---

## 🔴 #2 — `apply_patch`, not `Edit`/`Write`

- One structured **patch blob**: Add/Update/Delete across many files at once.
- A real grammar (`apply_patch.lark`) + `seek_sequence` → **context-matched**,
  so drifted line numbers don't matter.
- CC's `Edit` is exact-substring find-and-replace: simpler, but ambiguous when
  the target isn't unique and brittle to whitespace.

The edit is a **reviewable object before it touches disk** — diff UI and sandbox
checks compose on it.

`▶ examples/02_apply_patch.py` · `▶ diagrams/02_apply_patch_vs_edit.svg`

---

## 🔴 #3 — Code mode

The model can **write a program that calls tools**, instead of one JSON call at
a time:

```python
for p in list_dir("src/"):
    write_file(p, "# audited\n" + read_file(p))   # N calls, ONE turn
```

Tools are rendered as a typed API; each call becomes a **nested tool call**.
No Claude Code equivalent (CC is pure JSON function-calling).

`▶ examples/04_code_mode.py` · `▶ diagrams/03_code_mode.svg`

---

## 🔴 #4 — Guardian / `auto_review`

When no human can be in the loop (CI, cloud), Codex can route an approval to a
**risk-assessing AI subagent** that approves/denies sandbox escapes & network.

- **Codex:** delegate the *judgment* to another agent.
- **Claude Code:** write a deterministic `PreToolUse` **hook** (rules).

Two answers to "who says yes" — judgment vs rules.

---

## 🔴 #5 — Rust binary, voice & cloud

- **Rust single binary** (Node is just a launcher) → *why* kernel sandboxing can
  be the default; CC's Node leans on prompts.
- **Realtime voice (WebRTC)** and **`cloud-tasks`** — surfaces with no CC analogue.
- Same SQ/EQ engine, radically different I/O — proof the protocol-first design pays off.

---

## What you can safely skim 🟢

These are ~the same as Claude Code — learn once, reuse:

- the agent loop (Session/Thread/Turn)
- tool registry & router · parallel tool calls
- context manager & compaction
- MCP client + server · hooks · skills
- subagents · session resume · `AGENTS.md` (≈ `CLAUDE.md`)

`▶ examples/01_sqeq_loop.py` · `▶ examples/05_tool_registry.py`

---

## The capstone: one prompt, end to end

1. surface → **Submission** 🟢
2. Turn opens, **Responses API** streams tool calls 🔴
3. maybe **code mode** scripts several calls 🔴
4. edits arrive as **apply_patch** 🔴
5. command runs **sandboxed by default** 🔴 → on escape, **escalate** to human/**guardian** 🔴
6. **compaction** may fire; every event appended to the **rollout** 🟡
7. loop repeats → **turn complete** → answer (terminal / JSONL / SDK / **voice** 🔴)

The loop never changed. That discipline *is* harness engineering.

---

# Go build

- Lessons: `lessons/`  ·  Diagrams: `diagrams/`  ·  Runnable: `examples/`
- All examples run offline, zero deps: `python3 examples/0X_*.py`

*"Trust the kernel, not the prompt" + "native, not Node" explains almost everything.*
