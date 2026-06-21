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
