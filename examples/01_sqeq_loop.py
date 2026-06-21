#!/usr/bin/env python3
"""
01_sqeq_loop.py — The Submission Queue / Event Queue spine  (Lesson L01)

Motto: An agent is a function from a Submission Queue (SQ) to an Event Queue (EQ).

Codex's whole engine is organized around this: clients push *Submissions*
(user message, approval response, interrupt) and the agent emits *Events*
(token delta, tool begin/end, approval request, turn complete). Every surface
— TUI, headless exec, SDK, even voice — is just a reader/writer of these queues.

    SUBMISSIONS                  EVENTS
    ─────────────                ──────────────────────
    UserInput      ──▶ [ LOOP ] ──▶ AgentMessageDelta
    Approval       ──▶          ──▶ ToolCallBegin / End
    Interrupt      ──▶          ──▶ ApprovalRequest
                                 ──▶ TurnComplete

This file is a *self-contained, offline* illustration — the "model" is a tiny
deterministic mock so you can run it with no API key and no dependencies.

Run:
    python3 examples/01_sqeq_loop.py
"""
from __future__ import annotations
import queue
from dataclasses import dataclass, field
from typing import Any


# ── The protocol: Submissions in, Events out ──────────────────────────────
@dataclass
class Submission:
    kind: str                 # "user_input" | "approval" | "interrupt"
    data: Any = None

@dataclass
class Event:
    kind: str                 # "delta" | "tool_begin" | "tool_end" | "approval_request" | "turn_complete"
    data: Any = None


# ── A mock model: returns a scripted plan of tool calls then a final answer ─
def mock_model(history: list[dict]) -> list[dict]:
    """Pretend to be an LLM. Returns a list of 'items' (tool calls / text)."""
    turn = sum(1 for m in history if m["role"] == "user")
    if turn == 1:
        return [{"type": "tool_call", "name": "shell", "args": "ls"},
                {"type": "text", "text": "Listed the directory."}]
    return [{"type": "text", "text": "Done."}]


# ── The loop: the one part nothing rewrites (L02) ──────────────────────────
def run_turn(history: list[dict], sq: queue.Queue, eq: queue.Queue) -> None:
    while True:
        items = mock_model(history)
        history.append({"role": "assistant", "content": items})
        tool_results = []
        for item in items:
            if item["type"] == "text":
                eq.put(Event("delta", item["text"]))
            elif item["type"] == "tool_call":
                eq.put(Event("tool_begin", item["name"]))
                # A risky tool would emit an approval_request and block on SQ.
                output = f"(ran `{item['args']}`)"
                eq.put(Event("tool_end", output))
                tool_results.append(output)
        if not tool_results:                 # model stopped calling tools
            eq.put(Event("turn_complete"))
            return
        history.append({"role": "user", "content": tool_results})


# ── A surface: anything that drains the EQ and renders it ──────────────────
def render(eq: queue.Queue) -> None:
    icons = {"delta": "💬", "tool_begin": "▶ ", "tool_end": "✓ ",
             "approval_request": "❓", "turn_complete": "■ "}
    while not eq.empty():
        ev = eq.get()
        print(f"  {icons.get(ev.kind, '?')} {ev.kind:16} {ev.data or ''}")


if __name__ == "__main__":
    sq: queue.Queue = queue.Queue()
    eq: queue.Queue = queue.Queue()
    history: list[dict] = []

    print("SQ/EQ loop — submit two user turns, watch the event stream:\n")
    for text in ["list the files", "thanks"]:
        print(f"SUBMISSION  user_input: {text!r}")
        history.append({"role": "user", "content": text})
        run_turn(history, sq, eq)
        render(eq)
        print()

    print("The TUI, `codex exec`, and the SDK differ ONLY in who writes SQ and reads EQ.")
