# Lessons — index

Per-lesson folders, mirroring `learn-claude-code`. Each folder has a `README.md`; 🔴 lessons that diverge from Claude Code also ship a runnable `code.py` and/or a diagram in `images/`.

> Legend: 🔴 divergent (focus) · 🟡 twisted · 🟢 same as Claude Code (skim).


## Stage 0 — Orientation & Stage 1 — The Loop

- [s00_shape_and_process_model](s00_shape_and_process_model/) — Shape & process model 🔴
- [s01_sqeq_protocol](s01_sqeq_protocol/) — SQ/EQ protocol & app-server 🟡
- [s02_session_thread_turn](s02_session_thread_turn/) — Session · Thread · Turn · TurnContext 🟢
- [s03_model_client](s03_model_client/) — Model client: Responses API, reasoning & providers 🔴
- [s04_prompt_assembly](s04_prompt_assembly/) — Prompt assembly & base instructions 🟢

## Stage 2 — Tools (how the model acts)

A tool = **a spec (what the model sees) + a handler (what runs) + a result (what feeds
back)**. Note in `core/src/tools/handlers/` that nearly every tool ships a `*.rs` handler
**and** a `*_spec.rs`.

- [s05_tool_registry](s05_tool_registry/) — The tool registry & router 🟢
- [s06_shell_unified_exec](s06_shell_unified_exec/) — Shell & unified exec 🟡
- [s07_apply_patch](s07_apply_patch/) — apply_patch vs Edit/Write 🔴
- [s08_code_mode](s08_code_mode/) — Code mode: calling tools by writing code 🔴
- [s09_parallel_orchestrator](s09_parallel_orchestrator/) — Parallel tool calls & the orchestrator 🟢
- [s10_auxiliary_tools](s10_auxiliary_tools/) — The auxiliary tools 🟢

## Stage 3 — Safety & Sandboxing 🔴 (the heart of the course)

- [s11_safety_philosophy](s11_safety_philosophy/) — Safety philosophy: sandbox-first vs approval-first 🔴
- [s12_os_sandboxes](s12_os_sandboxes/) — OS sandboxes: Seatbelt / Landlock / bubblewrap 🔴
- [s13_network_exec_policy](s13_network_exec_policy/) — Network & exec policy, Windows, proxy 🔴
- [s14_approvals_profiles](s14_approvals_profiles/) — Approvals, escalation & permission profiles 🔴
- [s15_guardian_auto_review](s15_guardian_auto_review/) — Guardian / auto-review: AI-reviewed approvals 🔴

## Stage 4 — Memory (mostly shared — skim, except L18)

- [s16_context_manager](s16_context_manager/) — Context manager & history 🟢
- [s17_compaction](s17_compaction/) — Compaction 🟢
- [s18_rollout](s18_rollout/) — Rollout & replayable sessions 🟡
- [s19_agents_md_skills](s19_agents_md_skills/) — AGENTS.md, skills & memories 🟢

## Stage 5 — Extensibility · Stage 6 — Surfaces · Stage 7 — Capstone


## Stage 5 — Extensibility

New capabilities arrive as **tools in the registry (L05) + events on the queue (L01)** —
never as new branches in the loop. This pattern is shared with Claude Code, so this stage is
mostly skim.

- [s20_mcp](s20_mcp/) — MCP: client & server 🟢
- [s21_hooks_plugins](s21_hooks_plugins/) — Hooks & plugins 🟡
- [s22_multi_agent](s22_multi_agent/) — Multi-agent orchestration & agent graph 🟡
- [s23_tui](s23_tui/) — The TUI 🟡
- [s24_exec_sdk](s24_exec_sdk/) — exec (headless/CI) & SDKs 🟢
- [s25_voice_cloud](s25_voice_cloud/) — Realtime voice (WebRTC) & cloud-tasks 🔴
- [s26_capstone](s26_capstone/) — One prompt, end to end + the divergence map 🔴
