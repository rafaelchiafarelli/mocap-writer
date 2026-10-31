# mocap-writer — open points

Everything still open, in one list, to pick the work up again (Rafael,
2026-10-25). Each point names the file that holds its detail; when a point
is settled, record the decision there and remove its line here. Bugs are
not listed: they are the backlog in `bugs/bugs.md`.

Settled on 2026-10-31 and removed from here: how agents write
proposals (through an MCP tool into the film's workflow database,
`workflow-link`); the agents' side of preprod-link, planned in
`mocap-preprod` `initiatives/preprod-link/`.

Settled on 2026-10-30 and removed from here: fountain-native settings/1,
scenes/5 and notes/1, done (`mocap-contracts` `v0.6.0`).

Settled on 2026-10-28 and removed from here: file-format, done (its five
`film.json` rules and the `bible` and `change` messages are in
`mocap-contracts` `v0.5.0`); how the film keeps its
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

- **workflow-link** (planned 2026-10-31), after `mocap-contracts`
  `v0.8.0` (`workflow-records`).

Rafael, 2026-10-31: finish every open initiative in one stretch; gates
that wait only on him are waived ("waive and close"); bugs are fixed only
when they get in the way. Every initiative planned before that
was done on 2026-10-31.

## Decisions for Rafael

- **Versioning** — what a version of the film is and where each part
  of the workflow records it (`versioning/versioning.md`).

## Work for another repository

- **Story structure** — models and beats wait for a later talk with an
  agent (story-structure study/1, in git history: git log --
  initiatives/story-structure).
- **Across repositories** — mocap-previz decision D8, where the Fountain
  parser lives, is open there. Proposal to bring to it:
  `trelby/fountain.py` already is that parser (no wx; accents, dual
  dialogue, notes, synopses, forced elements; tested on the same
  `sample_ptbr.fountain`), and with option A the writer can write the
  scene records itself. Not raised in mocap-previz yet.

## Gates waived (Rafael, 2026-10-31)

fountain-native (a real scene's round trip; numbering tried in the
editor), film-bible (Rafael on the neutral sample; the agents' half is in
preprod-link's gate) story-structure (the act panel on a script), spellcheck (Rafael's pt-BR scripts), import-to-film (a real PDF to a film), front-matter (Rafael on the sample), architecture (Rafael's read-through) and preprod-link (Rafael's sync on the sample; a specialist run):
closed without them. pdf-import's real-script import stays a film
session's.

## Known quirks (not bugs yet)

- A failed open leaves an empty new tab when the current one was touched
  (`trelby/trelbyctrl.as-built.md`, gotchas).
- `Config.cursorLine` / `cursorColumn` and `honorSavedPos` are left from
  `.trelby`: nothing saves or restores the cursor now. The settings record
  leaves the cursor out (Rafael, 2026-10-26: it is per-user state).
- Shot is written as upper case + two trailing spaces (Trelby's convention,
  confirmed 2026-10-25); other Fountain tools read it as Action.
