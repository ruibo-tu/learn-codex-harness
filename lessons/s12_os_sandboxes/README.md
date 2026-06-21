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
