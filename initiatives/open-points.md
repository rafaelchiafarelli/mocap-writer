# mocap-writer — open points

Everything still open, in one list, to pick the work up again (Rafael,
2026-10-25). Each point names the file that holds its detail; when a point
is settled, record the decision there and remove its line here. Bugs are
not listed: they are the backlog in `bugs/bugs.md`.

## Decisions for Rafael

**Scene numbers** — [scenes/1](fountain-native/epics/scenes/tasks/1-scene-ids-and-numbering.md)
- A deleted scene: leaves a gap, or an `OMITTED` heading as in production
  scripts?
- A scene moved by cut and paste: keeps its number?
- Inserting between `12` and `12A`: proposal is to report it instead of
  making `12AA`.
- A "renumber all" command for early drafts, run only by Rafael? It would
  rewrite every record that names a scene, since the number is the identity.

**Scene annotations and notes**
- Where an annotation's fields live: the whole annotation inside the
  Fountain note, or a short typed note pointing to a record. Option A of
  the file-format study (`[[fx:…]]`-style notes pointing to records by id)
  implies the second; **to confirm**
  ([file-format/study/1](file-format/epics/study/tasks/1-requirements.md),
  "Scene annotations").
- The span-note marker format, which then also carries the annotation kind
  ([notes/1](fountain-native/epics/notes/tasks/1-span-notes.md)); its
  "depends on scenes/1 (same hidden-marker mechanism)" is out of date:
  scenes have no hidden marker since 2026-10-25.
- Field catalog: approve, cut or extend the proposal, the four maps and the
  scene annotations ([film-bible/contract/1](film-bible/epics/contract/tasks/1-field-catalog.md)).
  Its two questions: do Dialogue and Parenthetical carry character
  directions too? Is a Shot always its own element, or can it also be an
  annotation on an Action ("the camera follows her")?

**File format** — [file-format](file-format/file-format.md)
- The id form and the default paths of the parts in `film.json`: the
  session proposes, Rafael confirms
  ([layout/1](file-format/epics/layout/tasks/1-root-index-and-ids.md)).
- How the film keeps its history: a study to run, then Rafael decides
  ([layout/2](file-format/epics/layout/tasks/2-history.md)).
- The fields of the script-settings record: the session proposes, Rafael
  confirms ([fountain-native/io/2](fountain-native/epics/io/tasks/2-script-settings.md)).

**Pre-production link** — [preprod-link](preprod-link/preprod-link.md)
- How agents write proposals: (a) they write `item.json` and the writer
  refuses an invalid file, or (b) a validating `bible propose` command;
  deferred to the mocap-preprod planning.
- Whether "needs review" becomes a stored state
  ([sync/3](preprod-link/epics/sync/tasks/3-affected-records.md)).

**Story structure** — [story-structure](story-structure/story-structure.md)
- The study is not started; Rafael picks a model after it.

**Across repositories**
- mocap-previz decision D8, where the Fountain parser lives, is open there.
  Proposal to bring to it: `trelby/fountain.py` already is that parser (no
  wx; accents, dual dialogue, notes, synopses, forced elements; tested on
  the same `sample_ptbr.fountain`), and with option A the writer can write
  the scene records itself. Not raised in mocap-previz yet.

## Work waiting on something else

- **`mocap-contracts` tasks, none planned yet:** `film.harpia` (root index
  and ids, for file-format/layout/1), `script_settings` (io/2),
  `bible.harpia` (film-bible/contract/2), `scene_index` (preprod-link
  contract/1).
- **file-format/layout/1** waits for `film.harpia` and the id form above;
  **layout/3** (missing files: warn and search) waits for layout/1.
- **fountain-native/io/2** waits for layout/1 and `script_settings`; the
  `io` epic cannot merge up until it is done.
- **film-bible** waits for scenes/1 and layout/1; links/2 also changes
  `find_prop_words` to runs of capitalized words (rule settled
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
  `.trelby`: nothing saves or restores the cursor now.
- Shot is written as upper case + two trailing spaces (Trelby's convention,
  confirmed 2026-10-25); other Fountain tools read it as Action.

## Housekeeping

- mocap-writer's `dev` has commits not pushed to `origin`; mocap-studio's
  submodule pointer for mocap-writer is not bumped.
- One session per clone: two sessions in this clone (2026-10-25) switched
  branches under each other.
