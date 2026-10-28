# mocap-writer — open points

Everything still open, in one list, to pick the work up again (Rafael,
2026-10-25). Each point names the file that holds its detail; when a point
is settled, record the decision there and remove its line here. Bugs are
not listed: they are the backlog in `bugs/bugs.md`.

Settled on 2026-10-28 and removed from here: how the film keeps its
history (a change log, file-format/layout/2); the `bible` message's shape
(film-bible/contract/2) and its go-ahead in `mocap-contracts`.

Settled on 2026-10-26 and removed from here: the id form and the default
part paths (file-format/layout/1); the scene-number open points
(fountain-native/scenes/1); the settings record's fields
(fountain-native/settings/1, was io/2); annotations kept out of the script
text, anchored by quote and shown by a button (fountain-native/notes/1);
the field catalog (film-bible/contract/1), with shots as annotations
numbered `S1`, `S2` per scene; "needs review" not stored
(preprod-link/sync/3).

## Ready to implement

- **spellcheck/pt-br/1** — the pt-BR spell checker: plan it against
  study/1's decision (VERO through Hunspell via `pyenchant`, 2026-10-27),
  then implement
  ([pt-br/1](spellcheck/epics/pt-br/tasks/1-ptbr-dictionary.md)).

## Decisions for Rafael

- **How agents write proposals** — (a) they write `item.json` and the
  writer refuses an invalid file, or (b) a validating `bible propose`
  command; deferred to the mocap-preprod planning
  ([preprod-link](preprod-link/preprod-link.md)).
- **Story structure** — study done 2026-10-26: an act is a marker only,
  with a panel of act sizes (epic `acts`); models and beats wait for a
  later talk with an agent (story-structure study/1, in git history:
  git log -- initiatives/story-structure).
- **Across repositories** — mocap-previz decision D8, where the Fountain
  parser lives, is open there. Proposal to bring to it:
  `trelby/fountain.py` already is that parser (no wx; accents, dual
  dialogue, notes, synopses, forced elements; tested on the same
  `sample_ptbr.fountain`), and with option A the writer can write the
  scene records itself. Not raised in mocap-previz yet.

## Work waiting on something else

- **`mocap-contracts` `film`** (root index and ids, for
  file-format/layout/1): **done** (2026-10-27), tag `v0.4.0` (initiative
  `film-root`). Its task lists five rules layout/1 left open, for Rafael
  (`film-root/epics/film-messages/tasks/1-film-harpia-done.md`, "Not
  decided"); `fixtures/film-v1/` with `invalid/expected.json` can be run
  by layout/1's tests too.
- **`mocap-contracts` tasks, none planned yet** (Rafael's go-ahead
  needed, another repository): `script_settings`
  (fountain-native/settings/1), `annotation` (fountain-native/notes/1), `scene_index`
  (preprod-link/contract/1), `change_set` (preprod-link/contract/2).
- **fountain-native/scenes/5** (a move and Renumber all rewrite the
  records that name scenes) waits for the first such records.
- **file-format/layout/1** pins `mocap-contracts` `v0.5.0` (the five rules
  the `film` task left open, decided 2026-10-28, layout/1);
  **layout/3**, **4** and **5** wait for layout/1.
- **fountain-native/settings/1** waits for layout/1 and `script_settings`.
- **fountain-native/notes/1** waits for `annotation` (scenes/1–4 done
  2026-10-27).
- **film-bible** waits for layout/1 and `bible` (scenes done 2026-10-27); links/2 also
  changes `find_prop_words` to runs of capitalized words (rule settled
  2026-10-25).
- **preprod-link** waits for film-bible.

## Gates left to a film session or to Rafael

- fountain-native: one real scene survives open → save → open
  byte-identical. The numbering behavior was approved on 2026-10-27
  (rules and choices, with the number now given when a heading is
  finished, scenes/6); Rafael tries it in the editor.
- story-structure (done 2026-10-26, its folder removed 2026-10-28): Rafael
  uses the act panel on a script and says it does what he wanted.
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
