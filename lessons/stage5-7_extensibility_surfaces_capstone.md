# Stage 5 — Extensibility · Stage 6 — Surfaces · Stage 7 — Capstone

> Tags: 🟢 read fast · 🟡 note the delta · 🔴 focus. Extensibility is mostly shared; the
> surfaces hold one more 🔴 (voice + cloud-tasks); the capstone ties the divergences together.

---

# Stage 5 — Extensibility

New capabilities arrive as **tools in the registry (L05) + events on the queue (L01)** —
never as new branches in the loop. This pattern is shared with Claude Code, so this stage is
mostly skim.

## L20 — MCP: client & server 🟢
**Motto: *Speak one open protocol and inherit an ecosystem of tools.***

**Where to look:** `rmcp-client/`, `mcp-server/`, `mcp/`, `core/src/mcp.rs`, `mcp_tool_call.rs`, `mcp_tool_exposure.rs`, `session/mcp.rs`.

**The mechanism.** Codex is both an MCP **client** (exposes external servers' tools to the
model) and an MCP **server** (other apps drive Codex over MCP). External tools flow through
the same registry/router/approval/sandbox path as builtins; namespacing prevents collisions.

**🟢 vs Claude Code.** CC is likewise an MCP client and server with the same composition
model. **Don't dwell** — MCP is industry-standard and the two implementations agree.

**The aha.** Standardize the extension boundary on an open protocol; a third-party tool
becomes indistinguishable from a native one.

## L21 — Hooks & plugins 🟡
**Motto: *Give users injection points at the lifecycle seams.***

**Where to look:** `hooks/` + `core/src/hook_runtime.rs` + `tools/hook_names.rs`, `core-plugins/` + `plugin/` + `core/src/plugins/`, `handlers/request_plugin_install.rs`.

**The mechanism.** **Hooks** fire user-defined commands at lifecycle moments (session start,
before/after turn, before/after tool) — see the `run_*_hook` calls in `turn.rs`. **Plugins**
bundle tools + skills + config, installable even on the model's request.

**🟡 vs Claude Code.** Both have a hooks system at similar seams — the *concept* is shared.
The **delta** to keep in mind ties back to L15: in CC, hooks are also the primary
*programmatic safety gate* (`PreToolUse` deny); in Codex, safety leans on the sandbox +
guardian, so hooks read more as customization/automation than as the security boundary.

**The aha.** Expose your lifecycle as named events; the seams you used internally become the
public extension API.

## L22 — Multi-agent orchestration & agent graph 🟡
**Motto: *A sub-agent is just another loop, reachable as a tool.***

**Where to look:** `core/src/agent/` (`registry.rs`, `role.rs`, `control.rs`, `builtins/`), `handlers/multi_agents.rs` + `multi_agents_v2/` + `agent_jobs/`, `session/multi_agents.rs`, `agent-graph-store/`, `agent-identity/`.

**The mechanism.** Codex spawns other agents, each with a **role** and **identity**, and
coordinates them; from the parent's view, delegating is a tool call, and each sub-agent runs
its own Session/Turn loop (L02). The **agent-graph-store** tracks relationships and jobs.

**🟡 vs Claude Code.** CC also delegates to subagents (the `Task`/Agent tool) — the
"sub-agent as a tool call" idea is shared. The **delta**: Codex formalizes it more — explicit
agent **identity**, **roles**, a persistent **graph store**, and a v2 job system — aimed at
longer-lived, multi-party orchestration. CC's subagents are lighter-weight and more
ephemeral.

**The aha.** You don't need a special framework: loops addressable as tools + durable threads
= orchestration. Codex just adds identity and a graph so the orchestration can persist.

---

# Stage 6 — Surfaces

One engine (SQ/EQ, L01) driven many ways — the payoff of protocol-first design.

## L23 — The TUI 🟡
**Motto: *The UI is a stateful reader of the event stream.***

**Where to look:** `tui/` — `app.rs`, `chatwidget.rs`, `bottom_pane/`, `diff_render.rs`, `app_event.rs`, `app_backtrack.rs`, `approval_events.rs`.

**The mechanism.** A render loop over the EQ: stream tokens, render `apply_patch` diffs
(L07), surface approval prompts (Stage 3) as dialogs, turn keystrokes into Submissions. It
holds view state, not agent logic.

**🟡 vs Claude Code.** Both are thin terminal UIs over the event stream. The **delta** is
purely technological: Codex's TUI is **Rust + ratatui** (immediate-mode, in the same binary
as the engine); CC's is **Node + Ink/React**. Same architecture, different rendering stack —
a direct consequence of L00.

**The aha.** Keep zero agent logic in the view; a second surface then costs almost nothing.

## L24 — exec (headless/CI) & SDKs 🟢
**Motto: *Same engine, a machine on the other end of the queue.***

**Where to look:** `exec/` (`lib.rs`, `event_processor_with_jsonl_output.rs`, `exec_events.rs`, `docs/exec.md`), `app-server/` + `app-server-protocol/` + `app-server-transport/`, `sdk/typescript/`, `sdk/python/` (+ `sdk/python/examples/`), `core-api/`.

**The mechanism.** `codex exec` runs non-interactively, streaming events as **JSONL** or
human text (approval policy locked down — no human to ask, which is exactly why L15's guardian
exists). The **app-server** wraps the engine in a versioned protocol over stdio/uds; the TS &
Python SDKs are thin clients (create thread, run turn, stream events, resume).

**🟢 vs Claude Code.** CC has the same trio — print/headless mode, and an Agent SDK
(TS & Python). **Don't dwell.** Same insight: interactive and headless are just two
`EventProcessor`s over one queue, and the internal protocol *is* the public API.

**The aha.** Build the protocol once; vary only the reader.

## L25 — Realtime voice (WebRTC) & cloud-tasks 🔴
**Motto: *The queue can carry audio and reach the cloud, not just terminal text.***

**Where to look:** `realtime-webrtc/` (+ `core/src/realtime_conversation.rs`, `realtime_context.rs`, `realtime_prompt.rs`), `cloud-tasks/` + `cloud-tasks-client/` + `cloud-config/`.

**The mechanism.** Two surfaces with no CC analogue:
- **Realtime voice** — a WebRTC stack (macOS-native audio) wiring a live voice conversation
  into the agent, with its own realtime prompt/context path in `core`.
- **cloud-tasks** — a TUI client to launch and monitor **Codex cloud** agents (the hosted
  Codex), so you can delegate a task from your terminal to the cloud and watch its diff.

**🔴 vs Claude Code.** Neither voice nor an in-CLI cloud-task client has a direct CC
counterpart. They show the SQ/EQ abstraction stretching to a real-time audio transport and a
remote-execution surface — the same engine, radically different I/O.

**The aha.** Once the agent is "a function over an event stream," the *transport* of that
stream is free to vary all the way to live audio and remote cloud workers.

---

# Stage 7 — Capstone

## L26 — One prompt, end to end + the divergence map 🔴
**Motto: *Trace one request through every layer, and watch where Codex and CC part ways.***

Follow a single "fix this bug" prompt and note each 🔴 fork:

1. **L01/L24** — a surface turns text into a **Submission** (🟢 same shape as CC).
2. **L02** — a **Turn** opens with a frozen **TurnContext** (🟢).
3. **L04** — prompt assembled from base + **AGENTS.md** (🟢, ≈ `CLAUDE.md`) + skills + tools.
4. **L03** — the **Responses API** client streams reasoning + tool calls (🔴 different API
   than CC's Messages).
5. **L05/L08** — router dispatches calls; the model may use **code mode** to script several
   tool calls at once (🔴 no CC equivalent).
6. **L07** — file changes arrive as one **apply_patch** blob (🔴 vs CC's `Edit`/`Write`).
7. **L11–L13** — *here is the big fork:* the command runs **inside Seatbelt/Landlock, network
   off, by default** (🔴). CC would typically **ask you first** instead.
8. **L14/L15** — only on a sandbox escape does it **escalate** — to the **human**, or to the
   **guardian AI reviewer** (🔴 vs CC's hook-based or human gate).
9. **L16/L17** — outputs grow history; **compaction** (incl. remote, 🟡) may fire mid-turn.
10. **L18** — every event is appended to the **rollout** (🟡 explicit event-sourcing);
    resumable.
11. Loop repeats until the model stops calling tools → **turn-complete** event → the surface
    (terminal, JSONL, SDK, or **voice**, 🔴) shows the answer.

**The aha — the course in two sentences.** *What's the same:* both Codex and Claude Code are
an untouched SQ→loop→EQ spine with tools, context management, MCP, hooks, subagents, and
multiple surfaces bolted on as wrappers — that architecture is settled, shared, and worth
learning once. *What's different, and why it matters:* Codex is a **Rust binary that defaults
to a kernel sandbox and edits via a patch grammar, can let the model program its tool use,
can delegate approvals to an AI reviewer, and reaches all the way to voice and cloud** — a
set of choices that all trace back to one stance, *"trust the kernel, not the prompt,"* and
one implementation decision, *"native, not Node."*

---

## Exercises (difference-focused)
- **Feel "sandbox-first":** run a command that writes outside the workspace under default
  settings and watch the escalation; compare to how CC would gate the same action.
- **Read two `.sbpl` files:** diff `seatbelt_base_policy.sbpl` vs `seatbelt_network_policy.sbpl`
  and write down exactly what each denies.
- **Trigger code mode:** find where tool schemas are rendered to TypeScript
  (`render_json_schema_to_typescript`) and trace one nested tool call through the runtime.
- **Compare edit protocols:** hand-write the same two-file change as (a) an `apply_patch`
  blob and (b) a sequence of CC `Edit` calls; note which fails more gracefully on a stale
  line number.
- **Find the guardian's prompt:** locate where `auto_review` builds its reviewer context in
  `core/src/guardian/` and decide what you'd trust it to auto-approve.
