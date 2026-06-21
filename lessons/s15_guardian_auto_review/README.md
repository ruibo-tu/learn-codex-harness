## L15 — Guardian / auto-review: AI-reviewed approvals 🔴
**Motto: *When a human can't be in the loop, put a risk-assessing agent there.***

**Where to look:** `core/src/guardian/`, `protocol/src/config_types.rs` (`ApprovalsReviewer`: `user` / `auto_review`, legacy `guardian_subagent`), `core/src/tools/network_approval.rs`, `auto_review_denials.rs` (in `tui/`).

**The mechanism.** Codex lets you *route approval requests to an AI subagent* instead of the
human. With `approvals.reviewer = auto_review`, a "carefully prompted subagent gathers
relevant context and applies a risk-based decision framework before approving or denying"
sandbox escapes, blocked network access, MCP prompts, and escalations (quoting the config
docs). It's a second model whose only job is to be the gatekeeper.

**🔴 vs Claude Code.** No direct CC equivalent. CC's programmatic gatekeeping is
**`PreToolUse` hooks** — deterministic code you write that returns allow/deny. Codex's
guardian is instead a **judgment-based AI reviewer**. Different trust model: CC says "write
rules"; Codex offers "delegate the judgment to another agent." Both exist so that automated/
headless runs don't deadlock on a human prompt.

**The aha.** Approval is itself an automatable role. Your options for "who says yes" are: the
human, deterministic rules (CC hooks), or a reviewing agent (Codex guardian) — and a mature
harness supports more than one because different deployments (interactive vs CI vs cloud)
need different gatekeepers.
