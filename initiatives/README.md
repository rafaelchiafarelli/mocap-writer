# mocap-writer — initiatives (execution order)

Source: Rafael's review of unmodified Trelby (2026-10-23). Known bugs live in
the **bugs** initiative (`bugs/bugs.md`), a backlog outside the order below:
each is fixed on a fix branch when it gets in the way.

**Open points** (decisions pending, work waiting, gates): `open-points.md`.

The as-built documentation (initiative 0, done 2026-10-24) lives with the
code: `../trelby.process.md` and a `CLAUDE.md` in each folder.

1. **pdf-import** — Rafael's existing PDF scripts open in the writer and come out as Fountain (done 2026-10-24; the gate's real-script import is left to a film session, Rafael's call; history: `git log -- initiatives/pdf-import`)
2. **editor-ux** — zoom, dark theme, Tab order, capitalized words in Action (done 2026-10-24; history: `git log -- initiatives/editor-ux`)
3. **fountain-native** — open/save Fountain as the native format; permanent scene numbers; notes on text spans
4. **file-format** — the one format that holds the script, the bible, notes, links and the rest: study done 2026-10-25, option A (a folder of Harpia JSON records, ISOXML-style; C, a change log in SQLite, kept in mind); next the root index and ids
5. **film-bible** — the maps (sets, characters, props, wardrobe) as folders in the film root
6. **preprod-link** — feed the mocap-preprod agents: scene index, Sync to spec (script-to-spec on every change), review of proposals
7. **story-structure** — where we are in the story (acts, beats): a study first

`film-bible` needs `fountain-native/scenes` (scene numbers). `preprod-link` needs `film-bible`. `film-bible`, `preprod-link` and `fountain-native/io/2` (per-script settings) need `file-format/layout/1`. `pdf-import` and `editor-ux` need nothing.
