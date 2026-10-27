## 1. Open and save Fountain natively

- **Status:** Done (2026-10-24) — `trelby/fountain.py`, wired into
  `MyCtrl.loadFile` / `saveFile`; as built: `trelby/fountain.as-built.md`

- **Type:** code
- **Depends on:** —
- **Contract:**
  - In: a `.fountain` file (spec 1.1, UTF-8)
  - Requires: File → Open/Save read and write Fountain directly (today it is
    import only, and saving writes `.trelby`); every element the editor has
    maps to Fountain (scene, action, character, dialogue, parenthetical,
    transition, shot, note, act break → section `#`), plus title page,
    scene numbers `#n#`, dual dialogue, boneyard and synopses kept as written;
    what the editor cannot show is kept and written back untouched
  - Delivers: Fountain as the default format; a round-trip guarantee
- **Pre-work:** —
- **Out of scope:** scene ids (scenes/1), span notes (notes/1)
- **Tests:** open → save → open is byte-identical on
  `mocap-previz/docs/exploration/script-to-previz/spikes/fountain/sample_ptbr.fountain`
  (copied in as a fixture) and on cases for every element, accents, dual
  dialogue, boneyard, synopses, title page
- **As built (2026-10-24):**
  - Unchanged elements, the title page and everything the editor does not
    show (boneyard, synopses, `##` sections, `===`, blank lines) are written
    back from the source read at open; edited and new elements are written
    in canonical Fountain, forced (`.` `!` `@` `>`) only when needed.
  - Save writes back to the file's own format; Save As proposes
    `.fountain`; Open lists `.fountain` and `.trelby`.
  - Elements Fountain cannot hold as they are (dialogue with no character,
    two dialogue elements in a row, ...) are listed in a warning after the
    save.
  - **Shot** is written as an upper-case line with two trailing spaces,
    Trelby's own convention (confirmed by Rafael, 2026-10-25); Fountain has
    no shot, so other tools (and mocap-previz) read it as Action.
  - **Not done here:** per-script settings are not saved in Fountain → io/2,
    now fountain-native/settings/1 (a record in the film root).
