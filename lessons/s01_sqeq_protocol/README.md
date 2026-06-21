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

## In this folder

- **`code.py`** — runnable demo (offline, no deps):
  ```bash
  python3 lessons/s01_sqeq_protocol/code.py
  ```
