## 1. Fountain import options

- **Status:** Scheduled (Rafael, 2026-10-31; was fountain-native/import/1,
  Future since 2026-10-26).
- **Why:** Import → Fountain reads a file exactly like Open
  (fountain-native/io/5). Upstream's importer, deleted in io/5, asked four
  options for Fountain written by other tools: import the title page, put
  title lines in as Action, strip emphasis markup (`*`, `**`, `_`), and
  turn sections (`#`) and synopses (`=`) into Note elements. Its last
  version is in git history: `git log -S importFountain --
  trelby/myimport.py` finds the io/5 commit that deleted it; its parent
  holds `importFountain`.

- **Type:** code
- **Depends on:** fountain-native/io/5 (done); front-matter/record/1 (the
  title page into the record)
- **Decided (Rafael, 2026-10-31):** four options: strip emphasis markup
  (`*`, `**`, `_`); sections (`#` below level 1) and synopses (`=`) as
  Note elements; title page lines as Action; the title page into the
  front matter record (when importing into a film; else it stays the
  script's title page, as Open does).
- **Contract:**
  - In: a `.fountain` chosen in Import, and the options the user ticks
    (all unticked by default except the title page into the record,
    ticked when there is a film).
  - Requires: the options change only how the file is turned into the
    script; nothing is guessed; the result is still written by
    `fountain.generate`.
  - Delivers: an options dialog on Import → Fountain, applied on top of
    `fountain.load` (no wx in the conversion: `fountain.importOptions`).
- **Pre-work:** none.
- **Tests:** each option on `tests/fixtures/fountain/elements.fountain`.
