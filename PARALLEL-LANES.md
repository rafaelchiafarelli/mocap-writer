# Parallel lanes — work for other sessions (2026-10-27)

Two lanes that run in their own clones while the original session works
on **fountain-native/scenes** in its own clone. Each lane follows the
`mocap-workflow` skill (`.claude/skills/mocap-workflow/SKILL.md`): one
initiative chain per clone, the task file is the contract, the full test
suite passes, the as-built docs travel with the change, and anything
outside the task's contract is a stop-and-ask.

**Not yours:** `initiatives/fountain-native/` and the scene-number code
(`trelby/fountain.py`, `trelby/screenplay.py`, `trelby/trelbyctrl.py`
for scene headings) belong to the scenes session. Don't edit them. If a
lane needs a change there, write it down and ask Rafael.

When a lane is done, its session deletes its section from this file in
its last merge to `dev`. The session that empties the file deletes it
and its bullet in `CLAUDE.md`.

---

## Lane C — mocap-contracts: the `film` message (`film.harpia`)

- **Repository / clone:** `mocap-contracts` (another repository), a new
  clone of its `dev`. Rafael gave the go-ahead (2026-10-27).
- **Why:** it unblocks `mocap-writer` file-format/layout/1 (root index and
  ids). That unblocks fountain-native/settings/1, file-format/layout/3
  and film-bible.
- **Source of the contract:** the "Decided" sections of
  `mocap-writer/initiatives/file-format/epics/layout/tasks/1-root-index-and-ids.md`:
  - `film.json`: `format_version` (int, 1), `origin` (`program`,
    `version`), `parts` (`name`, `path`, `owner`), `spaces` (`code`,
    `owner`);
  - the id form `<kind>-<space>-<n>` and its regex;
  - the kinds `set`, `character`, `prop`, `wardrobe`, `annotation`,
    `proposal`;
  - the `ids/<space>.json` counters (`next`, one entry per kind);
  - relative `/` paths that never leave the root and are never nested in
    another part's path.

  Also read `initiatives/file-format/epics/study/tasks/3-options.md` for
  option A (ISOXML-style).
- **First step is planning, not code:** there is no task for this in
  `mocap-contracts` yet. Create it the way that repository does
  (`mocap-contracts/initiatives/README.md`: a new initiative, epic and
  task file; `-done` file-name suffix; order between repositories in
  `mocap-studio/HANDOFF.md`). Write the message's fields, types and
  validation into the task file as its contract. Any field or rule that
  isn't decided in layout/1 goes to Rafael. **Never invent one.**
- **Then implement:** the `film` message (and the `ids` counter message,
  if the planning puts it in the same contract) in the schema, generated
  through Harpia's documented interface only. Add fixtures (a valid
  `film.json`; invalid ones that name the broken field) and tests. Tag a
  release as that repository does, so `mocap-writer` can pin it.
- **Out of scope:** the writer-side library (that is layout/1 in
  `mocap-writer`, done later); the `script_settings`, `bible`,
  `annotation`, `scene_index` and `change_set` messages (one task each,
  planned later, `film` first); any edit to `mocap-writer` except
  removing this section.
- **Done:** the task is merged up to `mocap-contracts` `dev` and tagged.
  In `mocap-writer`, on a `fixes/<next id>/…` branch: the `film` line
  under "Work waiting on something else" in
  `initiatives/open-points.md` says it is done, with the tag, and this
  section is removed.
