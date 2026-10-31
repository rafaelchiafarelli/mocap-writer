# mocap-writer — initiatives (execution order)

Source: Rafael's review of unmodified Trelby (2026-10-23). Known bugs live in
the **bugs** initiative (`bugs/bugs.md`), a backlog outside the order below:
each is fixed on a fix branch when it gets in the way.

**Open points** (decisions pending, work waiting, gates): `open-points.md`.

The as-built documentation (initiative 0, done 2026-10-24) lives with the
code: `../trelby.process.md` and a `CLAUDE.md` in each folder.

1. **pdf-import** — Rafael's existing PDF scripts open in the writer and come out as Fountain (done 2026-10-24; the gate's real-script import is left to a film session, Rafael's call; history: `git log -- initiatives/pdf-import`)
2. **editor-ux** — zoom, dark theme, Tab order, capitalized words in Action (done 2026-10-24; history: `git log -- initiatives/editor-ux`)
3. **fountain-native** — Fountain as the native format, permanent scene numbers (records follow moves), annotations outside the text, per-script settings in the film (done 2026-10-31, gate waived by Rafael; the import options moved to front-matter; history: git log -- initiatives/fountain-native)
4. **file-format** — the one format that holds the script, the bible, notes, links and the rest: a folder of Harpia JSON records (option A, `mocap-contracts` `film`/`bible`/`change`), the root index and ids, missing files, Open/New film, the change log (done 2026-10-28; history: git log -- initiatives/file-format)
5. **film-bible** — the maps (sets, characters, props, wardrobe) as folders in the film root: bible panel, one form per map from the catalog, scene/prop/wardrobe links, links by hand, copy (done 2026-10-31, gate waived by Rafael; history: git log -- initiatives/film-bible)
6. **preprod-link** — feed the mocap-preprod agents: scene index, Sync to spec (F5; change set, needs-review values), the review view (done 2026-10-31, gate waived; the agents' side is mocap-preprod's, in `open-points.md`; history: git log -- initiatives/preprod-link)
7. **story-structure** — where we are in the story: an act is a marker (no print) and a panel shows act sizes (done 2026-10-26, gate waived by Rafael 2026-10-31; models and beats later; history: git log -- initiatives/story-structure)
8. **spellcheck** — the spell checker in Brazilian Portuguese (pt-BR): VERO through Hunspell via `pyenchant`, the language chosen in Settings → Misc (done 2026-10-31, gate waived; history: git log -- initiatives/spellcheck)

9. **import-to-film** — an import ends in a complete film: Import into film (the original copied into `source/`), one review of the bible the script offers, a report; File → Import with a film open offers this film or a new folder (done 2026-10-31, gate waived; history: git log -- initiatives/import-to-film)

10. **architecture** — learn how mocap-writer is built: interactive explainer pages, a map and one page per layer, at https://claude.ai/artifact/KyZacNpzPJsvbTkca2gHAj (private) and in the repository since 2026-10-31 (`doc/architecture/` for people, `doc/architecture.md` for agents), built from the as-built docs at commit 959bc3c; when the code they explain changes they are rebuilt from the as-built docs, never edited from memory (done 2026-10-31, gate waived; history: git log -- initiatives/architecture)

11. **front-matter** — a film's title page and three optional pages (overview, pitch, argument) as a record, edited in a form, printed before the script, the Fountain title block written from it, and the Fountain import options (done 2026-10-31, gate waived; history: git log -- initiatives/front-matter)

12. **workflow-link** — the creator decides the agents' proposals and answers their requests in the review view, from the film's workflow database (planned 2026-10-31; needs `mocap-contracts` `v0.8.0`)

13. **versioning** — one versioning system for the whole workflow (asked by Rafael 2026-10-31; to be planned)

`film-bible` needs `fountain-native/scenes` (scene numbers). `preprod-link` needs `film-bible`. `film-bible`, `preprod-link` and `fountain-native/settings/1` (per-script settings, was io/2) need `file-format/layout/1`. `pdf-import`, `editor-ux` and `spellcheck` need nothing.
