## 1. Root index and id scheme

- **Type:** code, here and in `mocap-contracts`
- **Depends on:** study/3 (decision A); a `mocap-contracts` task for
  `film.harpia` (the root index and the id rules), done and tagged
- **Contract:**
  - In: a film root
  - Requires: `<film-root>/film.json`, a `film` message, as ISOXML's
    `TASKDATA.XML`: format version, origin (program and version that last
    wrote it), and the parts of the film (script, bible, settings, preprod,
    history...), each with its path and its **owner** (the writer, or a
    named agent), so no two programs write the same part; record ids are
    **typed and stable** (a prefix per kind: set, character, prop,
    wardrobe, annotation...) with a **separate id space per writer
    or agent**, so records made apart never collide (ISOXML's negative ids
    for terminal-made records); ids are never reused; a **scene has no
    record id**: it is named by its permanent scene number (`12A`,
    fountain-native/scenes/1, Rafael 2026-10-25); no record refers to
    another by path; a file that fails its Harpia message is refused with
    the path of the problem; **opening never breaks** (Rafael,
    2026-10-25): a missing or invalid part or file is collected into a
    list of problems (what, where it was expected, why) and the rest of
    the film opens; only a missing or invalid `film.json` stops the open,
    and then with a message, never a crash
  - Delivers: the library that opens a film root, validates `film.json`,
    tells a program which parts it owns, and hands out new ids
- **Pre-work:** Rafael confirms the id form and the default part paths
  (to propose); the `mocap-contracts` task above
- **Out of scope:** the warning and the search for missing files
  (layout/3); history (layout/2); the contents of each part (their
  own tasks); moving to C (study/3: kept in mind, not built)
- **Tests:** a new film root gets a valid `film.json`; two id spaces never
  collide; a part written by a program that does not own it is refused; an
  invalid file names the broken field; a film with a part and a photo
  deleted opens and lists both problems
