## 1. The numbering rule

The decisions below cover the whole `scenes` epic (tasks 1–5); this task
delivers the rule itself, without wx and without the editor.


- **Type:** code
- **Depends on:** io/1 (done)
- **Decision (Rafael, 2026-10-25):** scene numbers never change once given,
  because renumbering breaks every outside reference (breakdown, schedule,
  call sheets, take logs, people saying "scene 12"). A scene inserted later
  gets a letter: between 12 and 13 → `12.A`, then `12.B`, `12.C` (notation
  and nesting decided 2026-10-26, below). The number is
  **not editable**: a click on it shows a warning, with an option "do not
  show this again for the next 5 clicks". This replaces the earlier proposal
  of automatic renumbering with a hidden id.
- **Decisions (Rafael, 2026-10-26)** on the open points of 2026-10-25:
  - **Nesting:** levels alternate number and letter,
    `scene_number.scene_letter.scene_number.scene_letter...`, with a dot
    between every level: `12`, `12.A`, `12.A.1`, `12.A.1.A`. Not `12AA`,
    which gets complex quickly. Inserted between `12.A` and `12.B` →
    `12.A.1`; between `12.A.1` and `12.A.2` → `12.A.1.A`. Letters are all of
    `A`–`Z` (`I` and `O` included); after `Z` the next insert goes one level
    deeper (`12.Z.1`). Fountain 1.1 allows dots in scene numbers, so
    `#12.A.1#` is a valid heading.
  - **No room:** right after a scene and before its first child (between
    `12` and `12.A`, or `12.A` and `12.A.1`) no number fits. The writer
    reports it, offers Renumber all, and the scene stays unnumbered until
    Rafael renumbers or places it elsewhere; saving waits until every scene
    has a number.
  - **Delete:** the heading stays with its number and the word `OMITTED`
    (`#13# OMITTED`), as in production scripts; the number is never given
    again.
  - **Copy and move:** both give the pasted scene a new number by its
    position. A move (cut and paste) rewrites every record that named the
    old number (bible links, scene index, annotations) to the new one, as
    one undoable change; the old number is left `OMITTED`. A copy is a new
    scene and carries no links.
  - **Renumber all:** a command Rafael can run at any time, with a warning;
    it renumbers every scene `1, 2, 3...` in order and rewrites every
    record that names a scene, as one change. This relaxes the 2026-10-25
    "never change" for the records inside the film root; what is outside
    it (printed call sheets, people saying "scene 12") does not follow.
- **Decided in planning (2026-10-27, the epic split; Rafael can overturn):**
  - **A number is given when the script is saved** (task 3), the moment it
    can first be named outside the editor. Until then a new scene shows the
    number it will get, in parentheses (task 4). A scene made and removed
    between two saves leaves nothing.
  - **Before the first numbered scene** there is no room either (nothing
    comes before `1`): reported like "no room".
  - **Numbers in other forms** (`#1A#`, `#I-1-A#`, written by other tools)
    are kept as they are and stay unique; a scene inserted right after one
    of them has no room.
- **Contract:**
  - In: the scenes of a script in order, each with its number or none
  - Requires (new module `trelby/scenenumbers.py`, no wx):
    - `parse(s) -> tuple | None`: `"12.A.1"` → `(12, "A", 1)`; levels
      alternate number and letter, a dot between levels, a number has no
      leading zero, a letter is one of `A`–`Z`; anything else is `None`
      (another tool's form);
    - `assign(nums) -> (new, noRoom)`: `nums` is a list of `str | None`
      in script order; `new` is the same list with every `None` given a
      number by the rule, `noRoom` the indexes left `None`. The rule, for
      a new scene after `p` (the number before it, a new one included)
      and before `q` (the next existing number):
      - no scene numbered yet before or after: `1`, `2`, `3`...;
      - `q` none (at the end): the next whole number after the highest;
      - otherwise the next sibling of `p` (`12.A` → `12.B`,
        `12.A.1` → `12.A.2`) when `q` is outside `p`'s parent (so a
        whole number never gets the next whole number in the middle of
        the script: `12` → `12.A`); after `Z` there is no next letter;
      - otherwise `p`'s first child (`12` → `12.A`, `12.A` → `12.A.1`),
        unless `q` is a child of `p` (between `12` and `12.A`: no room);
      - `p` none (before the first numbered scene) or `p` in another
        tool's form: no room;
    - `check(nums) -> [Problem]`: duplicates (every index after the first
      of a number), numbers out of order, numbers in another tool's form,
      and scenes with no number; each problem names the scene index and
      the number;
    - `key(s)`: the sort key of a number in the writer's form.
  - Delivers: `trelby/scenenumbers.py` and its tests
- **Pre-work:** —
- **Touchpoint:** mocap-previz `fountain-input/2` writes
  `build/scenes/sc-<n>.json`; a dotted number (`sc-12.A.1.json`) is a safe
  file name, so nothing there changes.
- **Out of scope:** the editor, the file, the screen (tasks 2–4); INT/EXT
  prefixes (later)
- **Tests:** append → next whole number; a fresh script → `1..n`;
  insert after a whole number → letter; after a letter → next letter;
  between two letters → nested number, then nested letter; after `Z` one
  level deeper; several inserts in a row; between a scene and its child,
  before the first scene, after another tool's form → no room; `parse`
  of good and bad forms; `check` finds duplicates, order, foreign forms
  and missing numbers
