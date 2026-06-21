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

# Stage 6 — Surfaces

One engine (SQ/EQ, L01) driven many ways — the payoff of protocol-first design.
