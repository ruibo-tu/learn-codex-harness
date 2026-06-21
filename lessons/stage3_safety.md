# Stage 3 — Safety & Sandboxing 🔴 (the heart of the course)

> **This entire stage is the deepest divergence from Claude Code.** Read it long. The one
> idea: **Codex is sandbox-first — it runs your commands inside an OS kernel sandbox by
> default and only asks a human when the sandbox is escaped — whereas Claude Code is
> approval-first: it asks you (or consults a hook/allowlist) before acting, with sandboxing
> as a lighter, optional layer.**

---

## L11 — Safety philosophy: sandbox-first vs approval-first 🔴
**Motto: *Decide allow / sandbox / ask — and pick which one is your default.***

**Where to look:** `core/src/safety.rs` (+ `safety_tests.rs`), `core/src/tools/sandboxing.rs`, `core/src/shell.rs`, `shell-escalation/`, `protocol/src/config_types.rs` (`SandboxMode`: `ReadOnly`, `DangerFullAccess`, …), `docs/sandbox.md` → OpenAI security docs.

**The mechanism.** Before any command runs, `safety.rs` classifies it against the active
**sandbox mode** and **approval policy** and returns one of: run **sandboxed**, run
**unsandboxed** (trusted), or **escalate** (pause, emit an approval request on the EQ). The
default stance is: *run it sandboxed with no network; if the sandbox blocks it and that looks
intentional, escalate and ask the human to re-run with more access.* The sandbox modes
(`ReadOnly` → `workspace-write` → `DangerFullAccess`) are named, coarse stances.

**🔴 vs Claude Code — the core contrast.**

| | Codex (sandbox-first) | Claude Code (approval-first) |
|---|---|---|
| Default before running a command | Run it **inside the sandbox**, network off | **Ask the user** (or match an allowlist rule) |
| When does a human get prompted? | On **sandbox escape / denial** (escalation) | **Before** the action, by default |
| Primary enforcement | The **OS kernel** (Seatbelt/Landlock) | **Permission rules + the user's judgment**; hooks can deny |
| "Trust me, go fast" mode | `DangerFullAccess` / bypass sandbox | `bypassPermissions` mode |
| Programmatic gatekeeper | exec-policy + guardian subagent (L15) | `PreToolUse` hooks returning deny |

Both can reach the same end state; they differ in *what is the safety net by default*. Codex
trusts the kernel and treats human approval as the exception; CC trusts the human (and hooks)
and treats the sandbox as an add-on.

**The aha.** "Is the human in the loop by default, or is the kernel?" is the single most
consequential decision in agent safety design — and Codex vs CC are the two canonical
answers. Everything else in this stage is Codex executing on "the kernel."

---

## L12 — OS sandboxes: Seatbelt / Landlock / bubblewrap 🔴
**Motto: *Trust the OS kernel, not your own validation code.***

**Where to look:** `sandboxing/` — `seatbelt.rs` + `seatbelt_base_policy.sbpl`, `landlock.rs`, `manager.rs`, `policy_transforms.rs`, `restricted_read_only_platform_defaults.sbpl`; `linux-sandbox/`; `bwrap/`; `core/src/landlock.rs`.

**The mechanism.** Codex doesn't *parse commands to guess* safety — it runs them in a real
kernel sandbox:
- **macOS:** Apple **Seatbelt** (`sandbox-exec`) driven by a `.sbpl` profile granting
  read/write only to allowed roots.
- **Linux:** **Landlock** + **seccomp**, plus **bubblewrap** (`bwrap`) for namespacing.
- `manager.rs` + `policy_transforms.rs` compile Codex's *abstract* policy (writable roots,
  network on/off) into each platform's concrete profile.

**🔴 vs Claude Code.** This depth of *first-class, default, multi-platform kernel
sandboxing* is the standout Codex feature. CC has sandboxing options but they are lighter and
not the default enforcement path — CC primarily relies on the approval/allowlist model from
L11. Reading these `.sbpl` files is the best way to internalize what "sandbox-first" actually
buys you.

**The aha.** The strongest userspace sandbox is to delegate to the kernel: express one
abstract policy, compile it per-platform, let Seatbelt/Landlock enforce it. Hand-written
command validators always have holes.

---

## L13 — Network & exec policy, Windows, proxy 🔴
**Motto: *Filesystem, network, and the set of allowed programs are three separate locks.***

**Where to look:** `sandboxing/seatbelt_network_policy.sbpl`, `network-proxy/` + `core/src/network_policy_decision.rs` + `network_proxy_loader.rs`, `execpolicy/` + `execpolicy-legacy/` + `core/src/exec_policy.rs`, `windows-sandbox-rs/` + `core/src/windows_sandbox.rs`, `process-hardening/`.

**The mechanism.** Three more enforcement axes on top of L12:
- **Network policy** — off by default; when enabled, it can be funneled through a
  **proxy** (`network-proxy`) so access is *mediated*, not raw.
- **Exec policy** (`execpolicy`) — a declarative allow/deny layer for *which programs and
  argument shapes* may run, evaluated before spawn.
- **Windows** — a *separate* sandbox implementation, proving the L12 abstraction survives a
  hostile third platform.

**🔴 vs Claude Code.** Several of these have no real CC counterpart: a **declarative exec
DSL** (`execpolicy`), a **network proxy** as a core component, and a bespoke **Windows
sandbox**. CC controls programs/network through permission rules and the OS it runs on,
rather than a dedicated policy engine + proxy.

**The aha.** "Sandbox" is multi-dimensional — files, network, *and* the executable set —
each defaulting to least privilege and widened only by explicit policy.

---

## L14 — Approvals, escalation & permission profiles 🔴
**Motto: *Bundle dozens of safety knobs into a few nameable stances — and make "ask" a real return value.***

**Where to look:** `protocol/src/permissions.rs`, `protocol/src/models.rs` (`PermissionProfile`, `ActivePermissionProfile`, `SandboxEnforcement`), `protocol/src/config_types.rs` (`ModeKind`, `CollaborationMode`), `collaboration-mode-templates/`, `core/src/tools/handlers/request_permissions.rs`, `tui/src/collaboration_modes.rs`.

**The mechanism.** All the L11–L13 knobs collapse into **permission profiles** /
**collaboration modes** — named presets (read-only, workspace-write, full-access) selected in
the TUI and frozen into the `TurnContext`. The model can *request* an upgrade via
`request_permissions`, which the user grants/denies; an escalation pauses the turn and flows
through the same EQ as everything else.

**🔴/🟡 vs Claude Code.** Same *spirit* as CC's **permission modes** (`default`,
`acceptEdits`, `plan`, `bypassPermissions`) — both give users a few coherent stances instead
of twenty toggles. The **divergence** is what a mode *controls*: a Codex mode primarily sets
*sandbox + network + escalation* behavior (because the kernel is the enforcer); a CC mode
primarily sets *how eagerly it prompts you* (because you are the enforcer). Same UX idea,
opposite thing being configured.

**The aha.** Collapse your security surface into a few named stances, keep one active per
turn, and require an explicit, auditable request to change it.

---

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
