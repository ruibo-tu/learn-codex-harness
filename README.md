# Learn Codex — Reading OpenAI's Coding Agent as a Harness

A guided tour of [`openai/codex`](https://github.com/openai/codex), built the same way
[`shareAI-lab/learn-claude-code`](https://github.com/shareAI-lab/learn-claude-code) teaches Claude Code:

> **One agent loop stays untouched at the center. Each lesson adds exactly one harness
> mechanism around it. Each mechanism gets a motto.**

**This edition is *difference-weighted*.** If you already understand Claude Code (CC), you
don't need a second full tour of the parts that are the same. So every lesson is tagged with
how much it diverges from CC, and the course spends its words where the two systems actually
differ — and skims where they agree.

> **A note on fairness.** Codex is open source (we read its real files). Claude Code is
> **closed source**, so every "vs CC" claim here is based on Claude Code's *documented and
> observable* behavior plus the `learn-claude-code` teaching model — not its source. Treat
> CC comparisons as architecture-level, not line-level.

## Divergence legend

| Tag | Meaning | How to read it |
|---|---|---|
| 🔴 **Divergent** | Codex does this fundamentally differently than CC | **Spend your time here.** |
| 🟡 **Twisted** | Same idea, meaningfully different shape | Skim, note the twist. |
| 🟢 **Same** | Architecturally equivalent to CC | Read for completeness; don't dwell. |

---

## The 60-second difference map

The single sentence: **Codex is a Rust binary that runs your commands *inside an OS kernel
sandbox by default and asks only on escape*; Claude Code is a Node program that *asks you
before it acts* by default.** Almost every other divergence flows from that and from the
implementation language.

| Dimension | Codex | Claude Code | Tag |
|---|---|---|---|
| Implementation | Rust, single static binary (Node is just a launcher) | TypeScript/Node | 🔴 |
| Default safety posture | **Sandbox-first**: run in Seatbelt/Landlock, network off, escalate on denial | **Approval-first**: prompt the user / allowlist, sandbox optional | 🔴 |
| OS sandbox | First-class: Seatbelt, Landlock+seccomp, bubblewrap, Windows sandbox | Lighter / optional | 🔴 |
| File edits | `apply_patch` — a real **patch grammar** | `Edit`/`Write`/`MultiEdit` — **string replacement** | 🔴 |
| Tool-calling | JSON function calls **+ "code mode"** (model writes TS that calls tools) | JSON function calls only | 🔴 |
| Approval reviewer | Can route approvals to a **`guardian` AI subagent** (`auto_review`) | Human, or programmatic `hooks` | 🔴 |
| Model API | OpenAI **Responses API** (+ reasoning items) | Anthropic **Messages API** | 🟡 |
| Provider abstraction | OpenAI, Azure, OSS, ollama, lmstudio, proxy | Anthropic, Bedrock, Vertex | 🟡 |
| Extra surfaces | **Realtime voice (WebRTC)**, **cloud-tasks** client | — | 🔴 |
| Persistence | Explicit **rollout** event log (event-sourced, resumable) | Session transcripts (resume/continue) | 🟡 |
| Permission presets | "collaboration modes" / permission profiles | permission modes (default/acceptEdits/plan/bypass) | 🟡 |
| Project instructions | `AGENTS.md` | `CLAUDE.md` | 🟢 |
| MCP, hooks, skills, compaction, plan/todo, subagents, multi-surface | present, ~same idea | present, ~same idea | 🟢 |

Pin this mental model the whole way through — it's identical in *both* systems, which is
exactly why the loop itself is 🟢 and the **wrappers** are where the action is:

```
   user input ──▶ Submission Queue (SQ) ──▶ [ THE LOOP ] ──▶ Event Queue (EQ) ──▶ surface
                                                │
              everything else is a wrapper around this ──┘
       tools · sandbox · approvals · context · memory · MCP · multi-agent · surfaces
```

---

## Curriculum (topics + order, with divergence tags)

### Stage 0 — Orientation
- **L00 — Shape & process model** 🔴 — Rust single binary vs Node; the crate map.

### Stage 1 — The Loop (mostly shared — skim)
- **L01 — SQ/EQ protocol & app-server** 🟡
- **L02 — Session · Thread · Turn · TurnContext** 🟢
- **L03 — Model client: Responses API, reasoning & providers** 🔴
- **L04 — Prompt assembly** 🟢

### Stage 2 — Tools (how the model acts — two big divergences here)
- **L05 — Registry & router** 🟢
- **L06 — Shell & unified exec** 🟡
- **L07 — apply_patch vs Edit/Write** 🔴
- **L08 — Code mode: calling tools by writing code** 🔴
- **L09 — Parallel calls & orchestrator** 🟢
- **L10 — Auxiliary tools** (plan, ask-user, web, view) 🟢

### Stage 3 — Safety (the deepest divergence — the heart of the course)
- **L11 — Safety philosophy: sandbox-first vs approval-first** 🔴
- **L12 — OS sandboxes: Seatbelt / Landlock / bubblewrap** 🔴
- **L13 — Network & exec policy, Windows, proxy** 🔴
- **L14 — Approvals, escalation & permission profiles** 🔴
- **L15 — Guardian / auto-review: AI-reviewed approvals** 🔴

### Stage 4 — Memory (mostly shared — skim)
- **L16 — Context manager & history** 🟢
- **L17 — Compaction** 🟢
- **L18 — Rollout & replayable sessions** 🟡
- **L19 — AGENTS.md, skills & memories** 🟢

### Stage 5 — Extensibility (mostly shared)
- **L20 — MCP: client & server** 🟢
- **L21 — Hooks & plugins** 🟡
- **L22 — Multi-agent orchestration & agent graph** 🟡

### Stage 6 — Surfaces
- **L23 — The TUI** 🟡
- **L24 — exec (headless/CI) & SDKs** 🟢
- **L25 — Realtime voice (WebRTC) & cloud-tasks** 🔴

### Stage 7 — Capstone
- **L26 — One prompt end-to-end + the divergence map** 🔴

---

## Layout

One folder per lesson under [`lessons/`](lessons/) — mirroring `learn-claude-code`. Every
folder has a `README.md`; the 🔴 lessons that diverge from Claude Code also ship a runnable
`code.py` and/or a diagram in `images/`. Start at the [lessons index](lessons/README.md).

```
lessons/
  s00_shape_and_process_model/  README.md  images/overview.svg
  s01_sqeq_protocol/            README.md  code.py
  s05_tool_registry/            README.md  code.py
  s07_apply_patch/              README.md  code.py  images/apply_patch_vs_edit.svg
  s08_code_mode/                README.md  code.py  images/code_mode.svg
  s11_safety_philosophy/        README.md  code.py  images/safety_decision.svg
  s26_capstone/                 README.md  images/divergence_map.svg
  ... (27 folders total)
slides/codex-harness.md         a Marp deck
Makefile                        make demo · make test · make list · make slides
```

### ▶️ Runnable demos (zero deps, offline, no API key)
```bash
make demo     # run all five code.py in order, with headers
make test     # smoke-test that each exits 0
make list     # print the 27-lesson curriculum
```
| Demo | Lesson | Tag | Shows |
|---|---|---|---|
| `s01_sqeq_protocol/code.py` | L01 | 🟡 | the SQ/EQ spine |
| `s07_apply_patch/code.py` | L07 | 🔴 | patch grammar vs `Edit` |
| `s11_safety_philosophy/code.py` | L11 | 🔴 | sandbox-first vs approval-first |
| `s08_code_mode/code.py` | L08 | 🔴 | the model writes a program that calls tools |
| `s05_tool_registry/code.py` | L05 | 🟢 | registry + bounded parallel dispatch |

Pure Python 3.8+ stdlib — the "model" is a deterministic mock so the focus stays on the
harness, not the LLM.

### 🖼️ Diagrams (layered SVGs: gray = shared with CC, amber = divergent)
- [overview](lessons/s00_shape_and_process_model/images/overview.svg) — one loop, many wrappers
- [safety_decision](lessons/s11_safety_philosophy/images/safety_decision.svg) — **sandbox-first vs approval-first** (the key one)
- [apply_patch_vs_edit](lessons/s07_apply_patch/images/apply_patch_vs_edit.svg) — patch grammar vs string replace
- [code_mode](lessons/s08_code_mode/images/code_mode.svg) — model writes a program that calls tools
- [divergence_map](lessons/s26_capstone/images/divergence_map.svg) — the whole Codex-vs-CC table, visual

### 📊 `slides/codex-harness.md` — a [Marp](https://marp.app) deck
Read it as Markdown, or `make slides` to render HTML (also `--pdf`/`--pptx` via marp-cli).

> **Scope note.** Codex is open source (these point at real files in `codex-rs/`). Claude
> Code is closed source, so every "vs CC" comparison is architecture-level, based on CC's
> documented behavior and the `learn-claude-code` teaching model. The `code.py` files are
> teaching reductions, not Codex's production code.
