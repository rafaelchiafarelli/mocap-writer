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
    wardrobe, scene, annotation...) with a **separate id space per writer
    or agent**, so records made apart never collide (ISOXML's negative ids
    for terminal-made records); ids are never reused; no record refers to
    another by path; a file that fails its Harpia message is refused with
    the path of the problem
  - Delivers: the library that opens a film root, validates `film.json`,
    tells a program which parts it owns, and hands out new ids
- **Pre-work:** Rafael confirms the id form and the default part paths
  (to propose); the `mocap-contracts` task above
- **Out of scope:** history (layout/2); the contents of each part (their
  own tasks); moving to C (study/3: kept in mind, not built)
- **Tests:** a new film root gets a valid `film.json`; two id spaces never
  collide; a part written by a program that does not own it is refused; an
  invalid file names the broken field
