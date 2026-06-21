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
