#!/usr/bin/env python3
"""
02_apply_patch.py — apply_patch vs Edit/Write  (Lesson L07, 🔴 divergent)

Motto: Edit files through a patch grammar, not string surgery.

Codex edits code by having the model emit ONE structured patch describing many
files/hunks at once. Claude Code instead uses Edit/Write (find-and-replace a
string). This file implements a *miniature* of Codex's apply_patch format and
contrasts it with the naive string-replace approach so you can feel the
difference: context-matching survives drifted line numbers; string-replace does
not, and is ambiguous when the target string is not unique.

The format (a simplified version of the real one in `codex-rs/apply-patch/`):

    *** Begin Patch
    *** Add File: greeting.py
    +def hi():
    +    return "hi"
    *** Update File: math.py
    @@ def add(a, b):
         # adds two numbers
    -    return a - b
    +    return a + b
    *** Delete File: old.py
    *** End Patch

Run:
    python3 lessons/s07_apply_patch/code.py
"""
from __future__ import annotations
from dataclasses import dataclass, field


# ── Parsing ────────────────────────────────────────────────────────────────
@dataclass
class Hunk:
    op: str                              # "add" | "update" | "delete"
    path: str
    add_lines: list[str] = field(default_factory=list)        # for add
    search: list[str] = field(default_factory=list)           # context + removed
    replace: list[str] = field(default_factory=list)          # context + added


def parse_patch(text: str) -> list[Hunk]:
    lines = text.splitlines()
    assert lines[0] == "*** Begin Patch", "patch must start with *** Begin Patch"
    hunks: list[Hunk] = []
    cur: Hunk | None = None
    for line in lines[1:]:
        if line == "*** End Patch":
            break
        if line.startswith("*** Add File: "):
            cur = Hunk("add", line.removeprefix("*** Add File: ")); hunks.append(cur)
        elif line.startswith("*** Update File: "):
            cur = Hunk("update", line.removeprefix("*** Update File: ")); hunks.append(cur)
        elif line.startswith("*** Delete File: "):
            hunks.append(Hunk("delete", line.removeprefix("*** Delete File: "))); cur = None
        elif line.startswith("@@"):
            continue                                          # context header, locating hint only
        elif cur and cur.op == "add":
            assert line.startswith("+")
            cur.add_lines.append(line[1:])
        elif cur and cur.op == "update":
            if line.startswith("+"):
                cur.replace.append(line[1:])
            elif line.startswith("-"):
                cur.search.append(line[1:])
            else:                                             # context (leading space)
                ctx = line[1:] if line.startswith(" ") else line
                cur.search.append(ctx); cur.replace.append(ctx)
    return hunks


# ── seek_sequence: find a contiguous block of lines (tolerates line drift) ──
def seek_sequence(haystack: list[str], needle: list[str]) -> int:
    if not needle:
        return -1
    for i in range(len(haystack) - len(needle) + 1):
        if haystack[i:i + len(needle)] == needle:
            return i
    return -1


# ── Apply, over an in-memory filesystem (a dict) ────────────────────────────
def apply_patch(fs: dict[str, str], patch: str) -> None:
    for h in parse_patch(patch):
        if h.op == "add":
            if h.path in fs:
                raise ValueError(f"Add File: {h.path} already exists")
            fs[h.path] = "\n".join(h.add_lines) + "\n"
        elif h.op == "delete":
            del fs[h.path]
        elif h.op == "update":
            lines = fs[h.path].splitlines()
            at = seek_sequence(lines, h.search)
            if at < 0:
                raise ValueError(f"Update File: {h.path}: context not found "
                                 f"(but note: we never referenced a line NUMBER)")
            lines[at:at + len(h.search)] = h.replace
            fs[h.path] = "\n".join(lines) + "\n"


# ── Demo ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fs = {
        "math.py": (
            "# utilities\n"
            "import sys\n"            # <- an extra line that would shift line numbers
            "\n"
            "def add(a, b):\n"
            "    # adds two numbers\n"
            "    return a - b\n"      # <- the bug
        ),
        "old.py": "# remove me\n",
    }

    patch = """*** Begin Patch
*** Add File: greeting.py
+def hi():
+    return "hi"
*** Update File: math.py
@@ def add(a, b):
     # adds two numbers
-    return a - b
+    return a + b
*** Delete File: old.py
*** End Patch"""

    print("=== apply_patch (Codex way): one blob, 3 files, context-matched ===\n")
    apply_patch(fs, patch)
    for path in sorted(fs):
        print(f"--- {path} ---\n{fs[path]}")
    print("greeting.py created, old.py deleted, the bug fixed by CONTEXT — "
          "the `import sys` line shifted numbers and it did not matter.\n")

    print("=== Contrast: the Claude-Code-style string Edit ===")
    print("""    Edit(file="math.py", old="return a - b", new="return a + b")

  Works here, but the failure modes differ:
   - If "return a - b" appears twice, Edit is ambiguous and errors;
     apply_patch disambiguates via the surrounding context block.
   - Edit matches exact substrings; whitespace/indent drift breaks it.
     apply_patch matches whole lines as a sequence, located anywhere.
  Same goal, different protocol — and that choice shapes the whole review UX.""")
