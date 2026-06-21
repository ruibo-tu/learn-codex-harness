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

# Stage 7 — Capstone
