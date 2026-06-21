#!/usr/bin/env python3
"""
03_sandbox_first_safety.py — sandbox-first vs approval-first  (Lessons L11-L15, 🔴)

Motto: Decide allow / sandbox / ask — and pick which one is your DEFAULT.

This is the deepest divergence between Codex and Claude Code:

  • Codex (sandbox-first): run the command INSIDE an OS kernel sandbox with
    network off by default; only pause to ask a human when the sandbox is
    *escaped* (e.g. a write outside the workspace).
  • Claude Code (approval-first): ask the human (or match an allowlist / run a
    hook) BEFORE acting; sandboxing is a lighter, optional layer.

Both can reach the same end state; they differ in what the *default safety net*
is — the kernel, or the human. This file models both decision engines so you
can run the same commands through each and watch where the human gets pulled in.

Run:
    python3 examples/03_sandbox_first_safety.py
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    RUN_SANDBOXED = "run sandboxed"
    RUN_TRUSTED = "run unsandboxed (trusted)"
    ASK_USER = "escalate → ask human"
    REJECT = "reject"


@dataclass
class Command:
    argv: str
    writes_outside_workspace: bool = False
    needs_network: bool = False


# A tiny exec-policy allowlist (L13): read-only commands never need escalation.
READONLY = {"ls", "cat", "grep", "git status", "pwd", "find"}


# ── Codex: sandbox-first ────────────────────────────────────────────────────
def decide_codex(cmd: Command, sandbox_mode: str = "workspace-write") -> Decision:
    if sandbox_mode == "danger-full-access":
        return Decision.RUN_TRUSTED
    if sandbox_mode == "read-only" and (cmd.writes_outside_workspace
                                        or cmd.argv.split()[0] not in {w.split()[0] for w in READONLY}):
        # would mutate under a read-only profile → must ask
        return Decision.ASK_USER
    # default workspace-write: run it in the sandbox; the sandbox itself blocks
    # escapes, and only an *escape attempt* escalates to a human.
    if cmd.writes_outside_workspace or cmd.needs_network:
        return Decision.ASK_USER          # sandbox would deny → escalate
    return Decision.RUN_SANDBOXED


# ── Claude Code: approval-first ─────────────────────────────────────────────
def decide_claude_code(cmd: Command, mode: str = "default",
                       allowlist: set[str] | None = None) -> Decision:
    allowlist = allowlist or set(READONLY)
    if mode == "bypassPermissions":
        return Decision.RUN_TRUSTED
    if any(cmd.argv.startswith(a) for a in allowlist):
        return Decision.RUN_TRUSTED       # pre-approved rule, no sandbox needed
    # anything not on the allowlist: ask the human up front, BEFORE running
    return Decision.ASK_USER


# ── Demo ────────────────────────────────────────────────────────────────────
def show(cmd: Command):
    c = decide_codex(cmd)
    cc = decide_claude_code(cmd)
    flag = "  <-- DIFFERENT" if c != cc else ""
    print(f"  {cmd.argv:34}  Codex: {c.value:28}  CC: {cc.value}{flag}")


if __name__ == "__main__":
    print("Same commands through both safety engines (default profiles):\n")
    show(Command("ls"))
    show(Command("grep -r TODO ."))
    show(Command("pytest -q"))                                  # writes in workspace
    show(Command("npm install", needs_network=True))            # needs network
    show(Command("rm ~/.ssh/id_rsa", writes_outside_workspace=True))

    print("""
Read the 'DIFFERENT' rows:
  • `pytest` (writes only in the workspace): Codex just runs it sandboxed —
    no human needed — while CC asks first because it is not on the allowlist.
    => Codex bothers you LESS for safe-but-not-allowlisted work.
  • `npm install` / writing outside the workspace: both pull in a human, but
    Codex does so as an ESCALATION (the sandbox would have blocked it anyway),
    whereas CC asks PRE-EMPTIVELY.

The lesson: 'who is the default safety net, the kernel or the human?' is the
single most consequential choice in agent safety design.""")
