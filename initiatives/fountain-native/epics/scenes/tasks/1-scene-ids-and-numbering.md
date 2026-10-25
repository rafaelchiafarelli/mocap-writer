## 1. Scene numbers: permanent, with letters for inserts

- **Type:** code
- **Depends on:** io/1
- **Decision (Rafael, 2026-10-25):** scene numbers never change once given,
  because renumbering breaks every outside reference (breakdown, schedule,
  call sheets, take logs, people saying "scene 12"). A scene inserted later
  gets a letter: between 12 and 13 → `12A`, then `12B`, `12C`. The number is
  **not editable**: a click on it shows a warning, with an option "do not
  show this again for the next 5 clicks". This replaces the earlier proposal
  of automatic renumbering with a hidden id.
- **Contract (proposal, open points marked):**
  - In: a scene heading created, pasted, moved or deleted
  - Requires:
    - a new scene at the end gets the next whole number after the highest;
      a scene inserted between two others gets the first free letter after
      the one before it (`12` → `12A`; `12A` → `12B`);
    - the number is written in the heading as Fountain's own `#12A#`, so it
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
    - **open:** a deleted scene leaves a gap, or an `OMITTED` heading as in
      production scripts;
    - **open:** copy → the copy gets a new number by its position; cut and
      paste (move) keeps its number?
    - **open:** insert between `12` and `12A` (proposal: `12AA` is avoided by
      giving `12A` only to the first insert after 12; a later insert before
      it is reported);
    - **open:** a "renumber all" command for early drafts, run only by
      Rafael; since the number is the identity, it would have to rewrite
      every record that names a scene, as one change.
  - Delivers: numbering, the warning, the rule for other repositories
- **Pre-work:** the open points answered, recorded in this file
- **Out of scope:** INT/EXT prefixes (later)
- **Tests:** append → next number; insert → letter; numbers never change on
  insert/delete/move; duplicate on paste; numbers survive the Fountain round
  trip; the warning's 5-click counter
