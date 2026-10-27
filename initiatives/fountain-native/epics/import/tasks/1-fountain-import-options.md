## 1. Fountain import options

- **Status:** Future — a feature for later, not scheduled (Rafael,
  2026-10-26).
- **Why:** Import → Fountain reads a file exactly like Open
  (fountain-native/io/5). Upstream's importer, deleted in io/5, asked four
  options for Fountain written by other tools: import the title page, put
  title lines in as Action, strip emphasis markup (`*`, `**`, `_`), and
  turn sections (`#`) and synopses (`=`) into Note elements. Its last
  version is in git history: `git log -S importFountain --
  trelby/myimport.py` finds the io/5 commit that deleted it; its parent
  holds `importFountain`.

- **Type:** code
- **Depends on:** io/5
- **Contract (draft, to be settled when scheduled):**
  - In: a `.fountain` chosen in Import, and the options the user picks.
  - Requires: the options change only how the file is turned into the
    script; nothing is guessed (every option asked, defaults shown); the
    result is still written by `fountain.generate`.
  - Delivers: an options dialog on Import → Fountain, applied on top of
    `fountain.load`.
- **Pre-work:** decide which options are still worth it: `fountain.load`
  already reads the title page and keeps sections and synopses (hidden),
  so emphasis markup and sections/synopses as Notes may be the only ones.
- **Tests:** each option on `tests/fixtures/fountain/elements.fountain`.
