## 6. A scene gets its number when its heading is finished

- **Status:** Done (2026-10-27). As built: a script with no number at all
  is numbered at once, the heading under the cursor included, so that
  heading does not end up after its successor.

- **Type:** code
- **Depends on:** 1–4 (done)
- **Decided (Rafael, 2026-10-27):** the number is given **when the scene
  heading is finished**, not on save (this replaces choice 1 of task 1's
  "Decided in planning"; choices 2–6 approved the same day).
- **Decided in planning (2026-10-27, from Rafael's answer; can be
  overturned):**
  - a heading is **finished** when it has text and the cursor is not in
    it: after Enter, Tab, an arrow key or a click elsewhere; a pasted
    heading is finished at once; the heading being typed shows the number
    it will get in parentheses, `(12.A)`;
  - a script opened or imported without numbers is numbered at once (its
    headings are finished), so it counts as changed;
  - before the first numbered scene there is room when that scene is not
    `1` (`[new, 2]` → `1`); before scene `1` there is still none (task 1,
    choice 2);
  - `OMITTED` is still written on save, for the numbers the script had
    when opened or last saved; a number given while typing and gone
    before a save leaves nothing, and can be given again.
- **Contract:**
  - In: the script after every change the editor shows (a command, a
    click, a paste, undo, redo)
  - Requires: `scenenumbers.numberFinished(sp)` gives every finished
    heading without a number its number by the rule (the same plan as
    `prepareSave`), never the heading holding the cursor; it changes only
    `Line.num`, so it adds no undo step and no undo step's line ranges
    move (an undo that brings back a heading from before its number gives
    it back without one, and leaving it numbers it again); the editor
    calls it before each screen update; `assign` gives `1` before a first
    number above `1`.
  - Delivers: `numberFinished`, the call in `MyCtrl.updateScreen`, the
    `assign` change, the open report's wording
- **Pre-work:** —
- **Out of scope:** OMITTED while editing (stays on save)
- **Tests:** typing a heading gives no number until Enter; Enter gives it;
  a click (cursor moved) gives it; a pasted heading is numbered at once;
  an unnumbered script is numbered `1..n` except the heading under the
  cursor, which gets `1` when left; no room leaves `?`; undo of Enter
  takes the number away, redo and leaving give it back; `assign([None,
  "2"])` → `1`, `assign([None, "1"])` → no room
