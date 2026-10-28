# mocap-writer — initiatives (execution order)

Source: Rafael's review of unmodified Trelby (2026-10-23). Known bugs live in
the **bugs** initiative (`bugs/bugs.md`), a backlog outside the order below:
each is fixed on a fix branch when it gets in the way.

**Open points** (decisions pending, work waiting, gates): `open-points.md`.

The as-built documentation (initiative 0, done 2026-10-24) lives with the
code: `../trelby.process.md` and a `CLAUDE.md` in each folder.

1. **pdf-import** — Rafael's existing PDF scripts open in the writer and come out as Fountain (done 2026-10-24; the gate's real-script import is left to a film session, Rafael's call; history: `git log -- initiatives/pdf-import`)
2. **editor-ux** — zoom, dark theme, Tab order, capitalized words in Action (done 2026-10-24; history: `git log -- initiatives/editor-ux`)
3. **fountain-native** — open/save Fountain as the native format (done); permanent scene numbers (done 2026-10-27, gate waits for Rafael); notes on text spans
4. **file-format** — the one format that holds the script, the bible, notes, links and the rest: a folder of Harpia JSON records (option A, `mocap-contracts` `film`/`bible`/`change`), the root index and ids, missing files, Open/New film, the change log (done 2026-10-28; history: git log -- initiatives/file-format)
5. **film-bible** — the maps (sets, characters, props, wardrobe) as folders in the film root: implemented 2026-10-28 (bible panel, one form per map from the catalog, scene/prop/wardrobe links, copy); the gate (Rafael on the neutral sample, the mocap-preprod agents reading the records) is open
6. **preprod-link** — feed the mocap-preprod agents: scene index, Sync to spec (script-to-spec on every change), review of proposals
7. **story-structure** — where we are in the story: an act is a marker (no print) and a panel shows act sizes (done 2026-10-26; the gate, Rafael using the act panel on a script, is in `open-points.md`; models and beats later; history: git log -- initiatives/story-structure)
8. **spellcheck** — the spell checker in Brazilian Portuguese (pt-BR): study done 2026-10-27 (VERO through Hunspell via `pyenchant`); next the dictionary language setting (pt-br/1)

9. **import-to-film** — an import ends in a complete film: Import into film, one review of the bible the script offers, a report (planned 2026-10-28; three decisions for Rafael in `import-to-film/import-to-film.md`)

`film-bible` needs `fountain-native/scenes` (scene numbers). `preprod-link` needs `film-bible`. `film-bible`, `preprod-link` and `fountain-native/settings/1` (per-script settings, was io/2) need `file-format/layout/1`. `pdf-import`, `editor-ux` and `spellcheck` need nothing.
