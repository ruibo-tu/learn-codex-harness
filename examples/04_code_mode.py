#!/usr/bin/env python3
"""
04_code_mode.py — calling tools by writing code  (Lesson L08, 🔴 divergent)

Motto: Sometimes the best tool call is a program that makes many tool calls.

Claude Code uses pure JSON function-calling: the model emits ONE tool call,
gets a result, emits the next. Codex also offers "code mode": tools are
presented to the model as a typed API, and the model responds by *writing a
program* that calls them. One model turn can then loop, branch, and chain many
nested tool calls — instead of a JSON ping-pong per call.

This file shows the two halves Codex implements:
  1. render tool JSON-schemas into a typed (TS-like) API surface
     (cf. `render_json_schema_to_typescript` in codex-rs/code-mode-protocol)
  2. run a code-mode "script", recording each call as a NESTED tool call event
     (cf. CodeModeNestedToolCall / ExecuteRequest in the same crate)

Run:
    python3 examples/04_code_mode.py
"""
from __future__ import annotations
from dataclasses import dataclass


# ── Tool specs (what the model is given) ────────────────────────────────────
TOOLS = {
    "read_file": {"params": {"path": "string"}, "returns": "string"},
    "write_file": {"params": {"path": "string", "contents": "string"}, "returns": "void"},
    "list_dir": {"params": {"path": "string"}, "returns": "string[]"},
}


# ── (1) Render JSON schema → a typed API the model can program against ───────
def render_typescript(tools: dict) -> str:
    out = ["// Tools available in code mode:"]
    for name, spec in tools.items():
        args = ", ".join(f"{p}: {t}" for p, t in spec["params"].items())
        out.append(f"declare function {name}({args}): {spec['returns']};")
    return "\n".join(out)


# ── (2) A runtime that records nested tool calls as events ──────────────────
@dataclass
class NestedCall:
    name: str
    args: dict


class CodeModeRuntime:
    def __init__(self, fs: dict[str, str]):
        self.fs = fs
        self.calls: list[NestedCall] = []

    def _api(self) -> dict:
        def read_file(path):
            self.calls.append(NestedCall("read_file", {"path": path}))
            return self.fs.get(path, "")
        def write_file(path, contents):
            self.calls.append(NestedCall("write_file", {"path": path, "contents": contents}))
            self.fs[path] = contents
        def list_dir(path):
            self.calls.append(NestedCall("list_dir", {"path": path}))
            return [k for k in self.fs if k.startswith(path)]
        return {"read_file": read_file, "write_file": write_file, "list_dir": list_dir}

    def execute(self, script: str) -> None:
        """The model's ONE response is this whole program."""
        exec(script, {"__builtins__": {"len": len, "print": print}}, self._api())


# ── Demo ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== (1) What the model sees — tools rendered as a typed API ===")
    print(render_typescript(TOOLS), "\n")

    fs = {"src/a.py": "x = 1\n", "src/b.py": "y = 2\n", "README.md": "# hi\n"}

    # In code mode, the model returns a PROGRAM, not a single JSON tool call:
    model_script = '''
for path in list_dir("src/"):
    body = read_file(path)
    write_file(path, "# audited\\n" + body)
'''
    print("=== (2) The model's single response is a program ===")
    print(model_script)

    rt = CodeModeRuntime(fs)
    rt.execute(model_script)

    print("=== Nested tool calls recorded from ONE model turn ===")
    for c in rt.calls:
        print(f"  • {c.name}({c.args})")
    print(f"\n{len(rt.calls)} tool calls issued in a single turn. In Claude Code's "
          "JSON mode that is\n~{} model round-trips; code mode collapses them into one."
          .format(len(rt.calls)))
