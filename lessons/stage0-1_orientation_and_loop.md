# Stage 0 — Orientation & Stage 1 — The Loop

> Tags: 🔴 Divergent (focus) · 🟡 Twisted (skim the delta) · 🟢 Same as Claude Code (read fast).

---

## L00 — Shape & process model 🔴
**Motto: *The language choice is an architecture choice.***

**Where to look:** top `README.md`, `codex-rs/` (97-crate Rust workspace), `codex-cli/bin/codex.js` (the launcher), `sdk/`, `docs/getting-started.md`.

**The mechanism.** Codex is a **single statically-linked Rust binary**. The npm package
`@openai/codex` (`codex-cli/`) is *only a launcher* that locates and execs the platform
binary — there is no agent logic in Node. The brain is the `core` crate; surfaces (`tui`,
`exec`, `app-server`) are thin.

**🔴 vs Claude Code.** This is the first real divergence and it ripples through everything:
- CC is a **Node/TypeScript** program; its agent logic *is* the JS process. Codex's agent
  logic is native code, and Node is disposable.
- Native code is *why* Codex can ship serious OS sandboxing (Stage 3): Seatbelt/Landlock/
  seccomp are kernel-level facilities far easier to drive from a single-process Rust binary
  than from a Node runtime that spawns child processes.
- Distribution differs: Codex ships per-platform binaries (and `brew install --cask`); CC
  ships an npm package. Codex even *self-invokes* its own binary for sub-tasks like
  `apply_patch` (see `CODEX_CORE_APPLY_PATCH_ARG1` in `apply-patch/src/lib.rs`).

The crate map you actually need (of ~97):

| Concern | Crate(s) | Divergence |
|---|---|---|
| Agent brain / loop | `core` | 🟢 |
| Wire protocol | `protocol`, `app-server-protocol` | 🟡 |
| Tools | `core/src/tools`, `apply-patch`, `code-mode`, `tools` | 🔴 |
| Sandbox | `sandboxing`, `linux-sandbox`, `windows-sandbox-rs`, `bwrap`, `execpolicy`, `network-proxy` | 🔴 |
| Safety review | `core/src/guardian`, `shell-escalation` | 🔴 |
| Persistence | `rollout`, `thread-store`, `message-history` | 🟡 |
| Extensibility | `mcp-server`, `rmcp-client`, `hooks`, `core-plugins`, `core-skills` | 🟢 |
| Surfaces | `tui`, `exec`, `app-server`, `realtime-webrtc`, `cloud-tasks` | mixed |

**The aha.** Before reading any agent, ask "what runs the loop, and in what language?" The
answer pre-decides which safety and performance designs are even available. Codex chose Rust
*so that* the kernel sandbox could be the default. CC chose Node *and therefore* leans on
approval prompts. Neither is wrong — but the language is upstream of the safety model.

---

## L01 — SQ/EQ protocol & app-server 🟡
**Motto: *An agent is a function from a Submission Queue to an Event Queue.***

**Where to look:** `protocol/src/protocol.rs` (its doc comment names the *"SQ (Submission
Queue) / EQ (Event Queue)"* pattern), `protocol/src/items.rs`, `app-server-protocol/`.

**The mechanism.** Clients push **Submissions** (user message, interrupt, approval response,
config change); the agent emits **Events** (token deltas, tool begin/end, approval requests,
turn-complete). Every surface is just a reader/writer of these queues.

**🟡 vs Claude Code.** CC also has a streaming harness and a machine-readable
`stream-json` mode, so the *concept* is shared. The **twist**: Codex elevates this into a
versioned, transport-bound public contract via the **`app-server`** (L24) — the same
protocol that runs the TUI is the SDK's wire protocol. CC's equivalent (the Agent SDK) is
more SDK-shaped than queue-shaped. Read this lesson for the *vocabulary* (SQ/EQ, items) you'll
use for the rest of the course; don't over-study it as a difference.

**The aha.** Define the message protocol before the program and every surface, persistence,
and multi-agent feature becomes "something that reads this stream."

---

## L02 — Session · Thread · Turn · TurnContext 🟢
**Motto: *Separate what persists (thread) from what's happening now (turn).***

**Where to look:** `core/src/session/session.rs`, `session/turn.rs`, `session/turn_context.rs`, `codex_thread.rs`, `thread_manager.rs`.

**The mechanism.** **Thread** = durable conversation; **Session** = live runtime;
**Turn** = one input→answer cycle; **TurnContext** = the *immutable* per-turn settings
(cwd, sandbox/approval policy, model, instructions), frozen at turn start so mid-turn config
changes can't cause inconsistent decisions. The inner loop in `turn.rs` is the "untouched
loop."

**🟢 vs Claude Code.** Architecturally the same as CC's loop: a conversation that persists,
turns that run model→tools→repeat, and per-turn frozen settings. **Don't dwell.** The one
detail worth keeping: `TurnContext` immutability is what makes the safety decisions in
Stage 3 deterministic — the same idea exists in CC.

**The aha.** Snapshot policy at the turn boundary; never read mutable global config inside a
running loop.

---

## L03 — Model client: Responses API, reasoning & providers 🔴
**Motto: *The wire format you target shapes the agent you can build.***

**Where to look:** `core/src/client.rs`, `client_common.rs`, `responses_retry.rs`, `stream_events_utils.rs`, `model-provider-info/`, `responses-api-proxy/`, `ollama/`, `lmstudio/`.

**The mechanism.** `client.rs` speaks OpenAI's **Responses API**, turning an SSE stream into
typed `ResponseEvent`s, with retry/backoff (`responses_retry.rs`) and a provider abstraction
(`model-provider-info`) that also targets Azure, OSS models, **ollama**, and **lmstudio**.

**🔴 vs Claude Code.** Same *job*, different *world*:
- **Responses API vs Messages API.** Codex is built around OpenAI's Responses API, whose
  first-class **reasoning items** and server-side state (e.g. remote compaction, L17) shape
  the design. CC targets Anthropic's **Messages API** with its own thinking/streaming model.
  The event types, the way reasoning is carried, and what the server remembers all differ.
- **Provider matrix differs.** Codex ships local-model paths (`ollama`, `lmstudio`) and a
  `responses-api-proxy`; CC's non-Anthropic story is Bedrock/Vertex. If you're porting ideas
  between them, the client layer is *not* swappable — it's the most API-coupled crate.

**The aha.** "Call the LLM" is provider-coupled. Quarantine it behind one client that emits
*your* normalized events, so the rest of the harness never learns whether it's talking to
Responses, Messages, or a local model.

---

## L04 — Prompt assembly & base instructions 🟢
**Motto: *The system prompt is computed, not written.***

**Where to look:** `client_common.rs` (the `Prompt` type), `core/prompts/`, `core/src/agents_md.rs`, `session/turn.rs` (the `build_*_injections` calls).

**The mechanism.** Each turn assembles the model input from layers: base instructions +
project instructions (`AGENTS.md`) + active skills + tool specs + history. The prompt is a
*render target* fed by many injection sources.

**🟢 vs Claude Code.** Essentially identical to how CC composes its system prompt from base
rules + `CLAUDE.md` + skills + tools. **Don't dwell.** Only delta worth noting: Codex's
injection sources include MCP tool exposure and connector/plugin injections wired right into
`turn.rs`; CC has the same notion under different names.

**The aha.** Add capabilities by adding injection sources, never by editing a giant prompt
literal.
