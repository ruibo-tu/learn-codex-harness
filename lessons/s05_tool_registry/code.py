#!/usr/bin/env python3
"""
05_tool_registry.py — registry, router & parallel orchestration  (Lessons L05/L09)

Motto: Tools are data; dispatch is a table lookup — so the loop never changes.

This mechanism is ~the same in Codex and Claude Code (🟢), but it is the
keystone that lets every other lesson "add one wrapper without touching the
loop", so it's worth seeing concretely. We model:
  • ToolName with an optional namespace (builtin vs mcp vs dynamic) — L05
  • a registry of {spec, handler} and a router that dispatches by name
  • a bounded-concurrency orchestrator for parallel tool calls — L09
  • adding a new tool requires editing NO control flow

Run:
    python3 lessons/s05_tool_registry/code.py
"""
from __future__ import annotations
import concurrent.futures as cf
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ToolName:
    name: str
    namespace: str | None = None          # e.g. "mcp:github" — prevents collisions
    def flat(self) -> str:
        return f"{self.namespace}/{self.name}" if self.namespace else self.name


@dataclass
class Tool:
    spec: dict
    handler: Callable[[dict], str]


class Registry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    def register(self, name: ToolName, spec: dict, handler: Callable[[dict], str]):
        self._tools[name.flat()] = Tool(spec, handler)        # registration = data
    def specs(self) -> list[dict]:
        return [t.spec for t in self._tools.values()]
    def get(self, flat: str) -> Tool:
        return self._tools[flat]


def route_and_run(reg: Registry, calls: list[tuple[str, dict]], max_parallel: int = 4):
    """The orchestrator: independent calls run concurrently, bounded."""
    results: list[str] = [""] * len(calls)
    with cf.ThreadPoolExecutor(max_workers=max_parallel) as pool:
        futs = {pool.submit(reg.get(name).handler, args): i
                for i, (name, args) in enumerate(calls)}
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()
    return results


# ── Handlers ────────────────────────────────────────────────────────────────
def h_shell(args):  time.sleep(0.2); return f"$ {args['cmd']} -> ok"
def h_read(args):   time.sleep(0.2); return f"read {args['path']} (42 lines)"
def h_search(args): time.sleep(0.2); return f"found 3 hits for {args['q']!r}"


if __name__ == "__main__":
    reg = Registry()
    reg.register(ToolName("shell"), {"name": "shell"}, h_shell)
    reg.register(ToolName("read_file"), {"name": "read_file"}, h_read)
    # An MCP tool from an external server — namespaced, same registry, same path:
    reg.register(ToolName("search", namespace="mcp:github"),
                 {"name": "search"}, h_search)

    print("Registered tools (the model sees these specs):")
    for t in reg.specs():
        print("  •", t["name"])

    calls = [("shell", {"cmd": "ls"}),
             ("read_file", {"path": "main.rs"}),
             ("mcp:github/search", {"q": "TODO"})]

    t0 = time.perf_counter()
    out = route_and_run(reg, calls)
    dt = time.perf_counter() - t0

    print(f"\nDispatched {len(calls)} calls in parallel in {dt:.2f}s "
          f"(serial would be ~{0.2*len(calls):.1f}s):")
    for r in out:
        print("  ", r)

    print("\nNote: adding the MCP tool touched the REGISTRY, not route_and_run() "
          "and not the\nagent loop. That is the whole point — 'one loop stays untouched'.")
