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
