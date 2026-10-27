## 1. Story structure study

- **Type:** study (no code)
- **Depends on:** —
- **Contract:**
  - In: structure models; Fountain sections and synopses
  - Requires: for each model, what the writer would show (act bar, beat
    markers, pacing per page) and what it needs in the file; licenses of any
    tool looked at
  - Delivers: options with trade-offs, added to this file, for Rafael to choose
- **Constraints from decisions made elsewhere (2026-10-26):**
  - **The script stays a clean screenplay** (Rafael): no ids, markers or
    structured data in the Fountain text, so it never reads like a
    programming language. Fountain's own sections (`#`) and synopses (`=`)
    are allowed (other tools understand them and they don't print); any
    other structure data lives in records outside the script and is shown
    on demand, as annotations are (fountain-native/notes/1).
  - **Scenes are named by their permanent scene number** (`12`, `12.A`,
    `12.A.1`; fountain-native/scenes/1); a structure record refers to
    scenes by number, never by position or a hidden id.
  - **Records live in the film root** as Harpia JSON records with ids
    `<kind>-<space>-<n>` (file-format/layout/1); a new kind such as `act`
    or `beat` is a change to `film.harpia` in `mocap-contracts`.
- **Pre-work:** —
- **Out of scope:** implementation
- **Tests:** —
