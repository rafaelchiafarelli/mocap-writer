## 3. Numbers given on save; OMITTED; Renumber all

- **Status:** Done (2026-10-27). As built: an `OMITTED` heading goes
  right before the next higher number, so a new scene put where a deleted
  one was is an insert after the scene before (`1`, `1.A`, `2 OMITTED`,
  `3`).

- **Type:** code
- **Depends on:** 1, 2
- **Contract:**
  - In: Save (and Save As, and saving on exit) of a script whose scenes
    have numbers, new scenes without one, and numbers that disappeared
  - Requires:
    - the numbers the script had when it was opened or last saved are
      remembered; on save, one that is no longer on a scene heading is
      put back as an `OMITTED` heading (text `OMITTED`, its number) at
      its place by number order; a number left on a line that is no
      longer a scene heading is removed from it;
    - every scene without a number gets one by `scenenumbers.assign`;
    - all of it is **one undo step**, made only when something changed;
    - a duplicate number or a scene with **no room** stops the save with
      a message naming the scenes, and offers **Renumber all**;
    - `OMITTED` is written as Fountain's forced heading `.OMITTED #13#`
      (`#13# OMITTED` would read as an act break);
    - **Script → Renumber all scenes**, with a warning: every scene,
      in order, gets `1, 2, 3...`; the `OMITTED` headings are removed
      (their numbers mean nothing after a renumber); one undo step.
  - Delivers: `scenenumbers.prepareSave(sp)` and `renumberAll(sp)`, the
    save path and the menu command
- **Pre-work:** —
- **Out of scope:** rewriting records (task 5); showing numbers (task 4)
- **Tests:** a new script saved → `1..n`; an appended scene → next
  number; an inserted scene → letter; a deleted scene → `.OMITTED #n#`
  in its place; a heading turned into Action → OMITTED; a scene made and
  removed between saves → nothing; cut and paste (a move) → OMITTED and a
  new number; copy → new number; no room and duplicates stop the save;
  one undo step brings back the state before the save; Renumber all and
  its undo
