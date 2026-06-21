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
