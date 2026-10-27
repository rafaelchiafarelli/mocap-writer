# mocap-writer — open points

Everything still open, in one list, to pick the work up again (Rafael,
2026-10-25). Each point names the file that holds its detail; when a point
is settled, record the decision there and remove its line here. Bugs are
not listed: they are the backlog in `bugs/bugs.md`.

Settled on 2026-10-26 and removed from here: the id form and the default
part paths (file-format/layout/1); the scene-number open points
(fountain-native/scenes/1); the settings record's fields
(fountain-native/settings/1, was io/2); annotations kept out of the script
text, anchored by quote and shown by a button (fountain-native/notes/1);
the field catalog (film-bible/contract/1); "needs review" not stored
(preprod-link/sync/3).

## Ready to implement

- **fountain-native/scenes/1** — permanent scene numbers
  ([scenes/1](fountain-native/epics/scenes/tasks/1-scene-ids-and-numbering.md)).

## Decisions for Rafael

- **How a shot number is written** — a dot alone is ambiguous with a
  nested scene number (`12.A.3`), so it needs a separator scene numbers
  never use ([film-bible/contract/1](film-bible/epics/contract/tasks/1-field-catalog.md),
  "Approved").
- **How the film keeps its history** — a study to run, then Rafael decides
  ([layout/2](file-format/epics/layout/tasks/2-history.md)).
- **How agents write proposals** — (a) they write `item.json` and the
  writer refuses an invalid file, or (b) a validating `bible propose`
  command; deferred to the mocap-preprod planning
  ([preprod-link](preprod-link/preprod-link.md)).
- **Story structure** — study done 2026-10-26: an act is a marker only,
  with a panel of act sizes (epic `acts`); models and beats wait for a
  later talk with an agent
  ([study/1](story-structure/epics/study/tasks/1-structure-study.md)).
- **Across repositories** — mocap-previz decision D8, where the Fountain
  parser lives, is open there. Proposal to bring to it:
  `trelby/fountain.py` already is that parser (no wx; accents, dual
  dialogue, notes, synopses, forced elements; tested on the same
  `sample_ptbr.fountain`), and with option A the writer can write the
  scene records itself. Not raised in mocap-previz yet.

## Work waiting on something else

- **`mocap-contracts` tasks, none planned yet** (Rafael's go-ahead
  needed, another repository): `film` (root index and ids, for
  file-format/layout/1), `script_settings` (fountain-native/settings/1),
  `bible` (film-bible/contract/2), `annotation` (fountain-native/notes/1),
  `scene_index` (preprod-link/contract/1), `change_set`
  (preprod-link/contract/2). `film` first: it unblocks layout/1.
- **file-format/layout/1** waits for `film`; **layout/3** (missing files:
  warn and search) waits for layout/1.
- **fountain-native/settings/1** waits for layout/1 and `script_settings`.
- **fountain-native/notes/1** waits for scenes/1 and `annotation`.
- **film-bible** waits for scenes/1, layout/1 and `bible`; links/2 also
  changes `find_prop_words` to runs of capitalized words (rule settled
  2026-10-25).
- **preprod-link** waits for film-bible.

## Gates left to a film session or to Rafael

- fountain-native: one real scene survives open → save → open
  byte-identical; Rafael approves the numbering behavior.
- pdf-import (done): the import of a real script was left to a film
  session.

## Known quirks (not bugs yet)

- A failed open leaves an empty new tab when the current one was touched
  (`trelby/trelbyctrl.as-built.md`, gotchas).
- `Config.cursorLine` / `cursorColumn` and `honorSavedPos` are left from
  `.trelby`: nothing saves or restores the cursor now. The settings record
  leaves the cursor out (Rafael, 2026-10-26: it is per-user state).
- Shot is written as upper case + two trailing spaces (Trelby's convention,
  confirmed 2026-10-25); other Fountain tools read it as Action.
