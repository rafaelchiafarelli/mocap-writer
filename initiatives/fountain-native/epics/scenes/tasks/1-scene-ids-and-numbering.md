## 1. Scene numbers: permanent, with letters for inserts

- **Type:** code
- **Depends on:** io/1
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
- **Contract:**
  - In: a scene heading created, pasted, moved or deleted
  - Requires:
    - a new scene at the end gets the next whole number after the highest;
      a scene inserted between two others gets the next free value at the
      level after the one before it (`12` → `12.A`; `12.A` → `12.B`;
      between `12.A` and `12.B` → `12.A.1`), per the nesting rule above;
    - the number is written in the heading as Fountain's own `#12.A#`, so it
      travels with the text and every Fountain tool shows it; mocap-previz
      `fountain-input/2` already uses the scene number as the identity;
    - numbers are unique in the script; on open, duplicates or missing
      numbers (edited in another tool) are reported, never fixed silently;
    - **the number is the scene's identity** (Rafael, 2026-10-25): there
      is no hidden id; every record outside the script (bible links, scene
      index, change sets, annotations, mocap-previz) refers to a scene by
      its number. It is unique within the film; it means nothing in another
      film, so copying a bible item to another film does not carry its
      scene links (film-bible links/4); the writer refuses to save while
      two scenes share a number;
    - a deleted scene leaves `#n# OMITTED`; a move and Renumber all
      rewrite the records that name the scenes they change, as one
      undoable change; "no room" is reported (decisions above).
  - Delivers: numbering, the warning, OMITTED, the record rewrite on move
    and Renumber all, the rule for other repositories
- **Pre-work:** — (the open points were answered 2026-10-26, above)
- **Touchpoint:** mocap-previz `fountain-input/2` writes
  `build/scenes/sc-<n>.json`; a dotted number (`sc-12.A.1.json`) is a safe
  file name, so nothing there changes.
- **Out of scope:** INT/EXT prefixes (later)
- **Tests:** append → next number; insert → letter, then nested number and
  letter; after `Z` one level deeper; no room → reported, save waits;
  numbers never change on insert/delete; delete → `OMITTED`; move → new
  number and records rewritten, one undo; copy → new number, no links;
  Renumber all → records rewritten; duplicate on paste; numbers survive the
  Fountain round trip; the warning's 5-click counter
