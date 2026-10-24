# mocap-writer — initiatives (execution order)

Source: Rafael's review of unmodified Trelby (2026-10-23). Known bugs live in
the **bugs** initiative (`bugs/bugs.md`), a backlog outside the order below:
each is fixed on a fix branch when it gets in the way.

The as-built documentation (initiative 0, done 2026-10-24) lives with the
code: `../trelby.process.md` and a `CLAUDE.md` in each folder.

1. **pdf-import** — Rafael's existing PDF scripts open in the writer and come out as Fountain (done 2026-10-24; film-session gate open)
2. **editor-ux** — zoom, dark theme, Tab order, capitalized words in Action (done 2026-10-24)
3. **fountain-native** — open/save Fountain as the native format; scene ids and numbering; notes on text spans
4. **film-bible** — the maps (sets, characters, props, wardrobe) as folders in the film root
5. **preprod-link** — feed the mocap-preprod agents: scene index, Sync to spec (script-to-spec on every change), review of proposals
6. **story-structure** — where we are in the story (acts, beats): a study first

`film-bible` needs `fountain-native/scenes` (scene ids). `preprod-link` needs `film-bible`. `pdf-import` and `editor-ux` need nothing.
