# tests — pytest suite for the screenplay model, import and reports

**Role:** Unit tests that run without a display: they build `Screenplay`
objects directly and never create the wx GUI. 115 tests.
**Entry points:** `docker/test.sh [pytest args]` (the Mocap Studio way: runs
`python -m pytest` in the `mocap-writer` image, `docker/test.sh:10-12`);
upstream also `pytest` / `make test` (`Makefile`) and the GitHub workflow.
**Inputs → Outputs:** `tests/fixtures/*` → pass/fail.

## Files
- `u.py` — helpers: `init()` (`misc.init(False)` + `util.init(False)`, once),
  `new()` (empty `Screenplay` with a fresh `ConfigGlobal`), `load(name)` /
  `loadString(s)` (fixture → `Screenplay`), `fixtureFilePath`
  (`tests/u.py:11-49`).
- `__init__.py` — empty; makes `tests.u` importable.
- Editing commands on `tests/fixtures/test.trelby`:
  - `test_addchar.py` — typing a space / non-breaking space at the end of
    a line;
  - `test_changetype.py` — changing the type of one or several selected
    elements (Tab, Shift-Tab, to Transition), and the full Tab and
    Shift-Tab cycles;
  - `test_copypaste.py` — `paste`;
  - `test_cut.py` — `getSelectedAsCD(doDelete=True)`;
  - `test_delete.py` — delete forward / backward, joining elements;
  - `test_join_elems.py` — forced line breaks around element splits and
    joins;
  - `test_movement.py` — every movement command (`tests/test_movement.py:6-136`);
  - `test_ismodified.py` — which commands mark the script changed.
- `test_validate.py` — `Screenplay._validate` catches each invariant
  violation; also loads the translations (`tests/test_validate.py:3-5`).
- `test_renderscreenplay.py` — PDF export with core fonts and with the
  custom TTF.
- `test_myimport.py` — `importCeltx` and `importTextFile` against
  `test.trelby`; replaces `wx` in `sys.modules` by a `Mock` before importing
  `myimport` (`tests/test_myimport.py:10-16`).
- `test_pdfimport.py` — PDF import (`trelby/pdfimport.py`): draws its PDFs
  with ReportLab at test time (`makePdf`, US Letter, Courier 12; no PDF
  committed). With the profile `fixtures/pdf/letter-test.toml`: expected
  Fountain with accented names, page furniture dropped, dialogue joined
  across a page break, margin and typed scene numbers → `#n#`, dual
  dialogue → `^`, `strict` stops with page and line, lenient reading
  (nearest indent, columns as one line) with `IMPORT:` notes, a character
  with no speech → issue and note, profile errors, every profile in
  `trelby/pdfprofiles/` parses, the CLI with `--trace`. With the layout
  **detected**: the same script as with the profile, title page, page
  numbers, margin scene numbers, numbered heading without INT./EXT.,
  Trelby's own PDF export of `test.trelby` (detected = `trelby-a4.toml`),
  `probe`, `report`. `myimport.importPdf` with `wx` and `misc.TextDlg`
  patched (asks nothing, report, error box, trace). Loads the translations
  itself.
- `test_scriptreport.py`, `test_scenereport.py`, `test_locationreport.py`,
  `test_characterreport.py` — each report's `generate()` returns a PDF.
- `test_locations.py` — `Locations.refresh`.
- `test_pagelist.py` — `PageList` formatting.
- `test_zoom.py` — `ConfigGlobal` zoom: steps, limits, snapping,
  `zoomScale`, config round trip, and the PML/PDF text ops unchanged by
  the zoom. The zoomed `wx.Font`s themselves need a display and are not
  tested. Loads the translations itself, so it runs alone.
- `test_theme.py` — `ConfigGlobal` themes: `DARK_COLORS` covers every color
  var, switching applies a theme's colors and keeps each theme's custom
  colors, the config round trip (light under `Color/…`, dark under
  `Dark/Color/…`), an old config loads as light, and a WCAG contrast of at
  least 4.5:1 for each dark text / background pair drawn on screen. Loads
  the translations itself.
- `test_propwords.py` — `propwords.find_prop_words`: positions, accents,
  one-letter words, punctuation, mixed case and digits, an all-caps line.
- `test_taborder.py` — `ConfigGlobal.tabOrder`: the default cycle and its
  wrap-around, elements outside the cycle, config round trip, `recalc`
  clean-up. Loads the translations itself.
- `test_keycode.py` — `util.eventKeyCode`: arrows and other non-character
  keys fall back to their `WXK_` code, characters keep their Unicode value.
- `test_wxnames.py` — every `wx.<name>` used in `trelby/` exists in the
  installed wxPython (names removed in wxPython 4 fail only when their
  dialog opens, bugs/editor/17); submodules and prefixes, and open bugs, are
  listed as exceptions.
- `test_util.py` — `util.replace`, `splitToWords`, `escapeStrings`; the file
  itself is ISO-8859-1 encoded.
- `execute_random_tests.py` — manual fuzzer: random command sequences on a
  `Screenplay`, saving failing sequences (`# ut:ignore`, not collected by
  pytest because of its name).

## Key facts / gotchas
- **`_` comes from `test_validate.py`**: it is the only test module that
  loads the translations (`tests/test_validate.py:5`), which installs `_` as
  a builtin. The whole suite passes; running a single test file such as
  `tests/test_cut.py` fails with `NameError: name '_' is not defined`. Bug: [bugs/tooling/1](../initiatives/bugs/epics/tooling/tasks/1-tests-underscore.md).
- `tests/test_myimport.py` swaps `sys.modules["wx"]` for a `Mock` at import
  time; modules imported earlier by other tests keep the real `wx`, so the
  result depends on import order. Nothing in the suite sets
  `TRELBY_TESTING` (`trelby/config.py:14`). Bug: [bugs/tooling/2](../initiatives/bugs/epics/tooling/tasks/2-tests-wx-mock-order.md).
- `execute_random_tests.py` still imports `u` and `screenplay` as top-level
  modules via `sys.path` (`tests/execute_random_tests.py:16-20`), the
  pre-package layout. Bug: [bugs/tooling/4](../initiatives/bugs/epics/tooling/tasks/4-random-tests-stale.md).
- PDFs are generated, not committed: Rafael's real PDFs hold film text and
  stay out of the repo (see
  `initiatives/pdf-import/epics/importer/tasks/1-pdf-importer.md`).
- Not covered by any test: the wx GUI (`trelbyframe`, `trelbyctrl`,
  `viewmode`, dialogs), `.trelby` save round-trip, Fountain/FDX/HTML/RTF/text
  export, Fountain/FDX/Astx/Fade In import, pagination results, undo/redo.
- Two `SyntaxWarning`s from `trelby/titles.py` appear in every run. Bug: [bugs/tooling/5](../initiatives/bugs/epics/tooling/tasks/5-titles-escapes.md).

## Touchpoints
- Tests: `trelby/screenplay.py`, `trelby/config.py`, `trelby/myimport.py`,
  `trelby/pdfimport.py`, `trelby/pdf.py`,
  the report modules, `trelby/locations.py`, `trelby/pagelist.py`,
  `trelby/util.py`.
- Run by: `docker/test.sh`, `.github/workflows/main.yml`.
