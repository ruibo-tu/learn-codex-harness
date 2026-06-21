## L07 — apply_patch vs Edit/Write 🔴
**Motto: *Edit files through a patch grammar, not string surgery.***

**Where to look:** `apply-patch/` crate (`parser.rs`, `streaming_parser.rs`, `seek_sequence.rs`), `core/src/apply_patch.rs`, `core/src/tools/handlers/apply_patch.rs`, `handlers/apply_patch.lark` (the grammar).

**The mechanism.** Codex defines a small **patch language** — `*** Add/Update/Delete File`
with context hunks — backed by a real grammar (`apply_patch.lark`) and both a batch and a
**streaming** parser. `seek_sequence.rs` locates each hunk's context in the live file so
edits apply even when line numbers drift. The edit is one structured, diffable, approvable
object.

**🔴 vs Claude Code.** This is a genuine philosophical fork in how an LLM edits code:
- **Codex = one patch format.** The model emits *one* `apply_patch` blob describing many
  files/hunks at once. Pros: atomic multi-file change, a single diff to review/approve,
  one grammar to validate, resilience to miscounted line numbers via context-matching.
- **Claude Code = a family of edit tools.** `Edit` (find-and-replace a unique string),
  `Write` (whole file), `MultiEdit` (several edits in one file). Pros: dead simple, no
  grammar; the model just supplies old→new strings. Cons: each edit is its own call, and
  uniqueness/whitespace matching is the failure mode instead of hunk context.
- **Consequence for the harness:** Codex's structured patch is *why* its diff rendering
  (L23) and sandboxed file-write checks compose so cleanly — the change is a first-class
  object before it touches disk. CC's string edits are validated more at apply time.

**The aha.** If your agent edits code, choosing the *edit protocol* (patch grammar vs
string replacement) is a top-level design decision — it dictates your review UX, your
failure modes, and how safety inspects changes.

---

## In this folder

- **`code.py`** — runnable demo (offline, no deps):
  ```bash
  python3 lessons/s07_apply_patch/code.py
  ```
- **`images/apply_patch_vs_edit.svg`** — diagram for this lesson.
