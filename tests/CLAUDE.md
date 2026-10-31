# tests — pytest suite for the screenplay model, import and reports

**Role:** Unit tests that run without a display: they build `Screenplay`
objects directly and never create the wx GUI. 385 tests.
**Entry points:** `docker/test.sh [pytest args]` (the Mocap Studio way: runs
`python -m pytest` in the `mocap-writer` image, `docker/test.sh:10-12`);
upstream also `pytest` / `make test` (`Makefile`) and the GitHub workflow.
**Inputs → Outputs:** `tests/fixtures/*` → pass/fail.

## Files
- `u.py` — helpers; importing it installs the builtin `_`
  (`tests/u.py:16`), so every test file also runs on its own; `init()` (`misc.init(False)` + `util.init(False)`, once),
  `new()` (empty `Screenplay` with a fresh `ConfigGlobal`), `load(name)`
  (a Fountain fixture through `fountain.load`, plus the script settings of
  the `.sconf` of the same name, `tests/u.py:45`), `withOldEnding(sp)`
  (puts back the ending `test.trelby` had and Fountain cannot hold: "Very."
  as its own dialogue, two empty Actions, "Very"; `tests/u.py:69`),
  `loadString(s)` (Fountain text), `fixtureFilePath` (`tests/u.py:36`).
- `__init__.py` — empty; makes `tests.u` importable.
- Editing commands on `tests/fixtures/test.fountain`:
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
- `test_film.py` — file-format/layout/1: a new film's `film.json`, ids
  per kind and per space, ownership refusals, the invalid `film.json`
  fixtures of `mocap-contracts` (`fixtures/film-v1/invalid/`) refused
  naming their field, a film with parts deleted opening with its problems,
  `problemsText`. The New film / Open film menu commands need a display:
  checked through the real window with stubbed dialogs (2026-10-28).
- `test_relink.py` — file-format/layout/3: a film whose parts moved into
  `archive/`: one found file's pattern finds the rest and the next open
  has no problems; nothing is written before an accept; skip keeps it
  listed; wrong kind and outside the film refused; `pattern` /
  `applyPattern`. `RelinkDlg` needs a display: checked through the real
  window with stubbed dialogs (2026-10-28).
- `test_changelog.py` — file-format/layout/5: create / update / delete
  each log one `Change` line, an unchanged write none, bookkeeping and the
  script none; revert of one author's changes, logged; a broken line is a
  problem.
- `test_bible.py` — film-bible/contract/2: round trip per map, child
  items, unknown field and wrong values refused, an item found by id after
  its folder was renamed by hand, rename / move / delete, slug clashes,
  files copied in and a missing one relinked, approving a proposal,
  links, invalid and misplaced items as problems, the `mocap-contracts`
  `bible-v1` fixture, the change log. The bible panel needs a display:
  checked through the real window (tree, New, Rename, move, View → Bible,
  2026-10-28).
- `test_bibleedit.py` — film-bible/maps/1-4: every catalog field of each
  map is in the form; edit → save → reopen per map (text, number, choice,
  list), an unchanged value not saved again, a bad number refused,
  approving a proposal changes its state only, TBD needs its trigger,
  per-scene values, links shown by name keep their notes, files added and
  removed. The `BibleForm` needs a display: checked through the real
  window (2026-10-28).
- `test_biblelinks.py` — film-bible/links: heading locations, a new
  location offered and never made, a known one linked, made sets linked,
  rename keeps the link, aliases, a set with no scene; the scene at a line
  and its items; props as runs offered never made, known props linked,
  made props linked, "not a prop" remembered, bible characters skipped,
  the run being typed left out; wardrobe links, gaps and unlink, wardrobe
  with no character; Find characters (speaker names, offered never made,
  known names and aliases linked, made ones linked); copy (files and children, new ids, original keeps its
  scenes), cross-film copy without scenes or item links, the warning's
  scenes.
- `test_clicks.py` — bugs/editor/14-16: the click counter (wxGTK's
  double-click after the second press), the word and the element a double
  and a triple click select. The real clicks checked through the window
  (2026-10-28).
- `test_scriptsettings.py` — fountain-native/settings/1: the writer's
  defaults equal `mocap-contracts`' `script-v1` fixture byte for byte;
  settings changed → record → reopened equal (title layout included); a
  title page edited elsewhere opens from Fountain with a problem; out of
  range refused; the film round trip with the script text unchanged and
  the record in the change log; an invalid record or none keeps the
  defaults. The menu path checked through the real window (2026-10-30).
- `test_scenes_moves.py` — fountain-native/scenes/5: a cut-and-pasted
  scene found as moved on save, an edited one not, Renumber all composed
  with a move, undo takes the pending moves back, the bible records follow
  (1 → 2 and 2 → 3 at once). The save path checked through the real
  window (2026-10-30).
- `test_annotations.py` — fountain-native/notes/1: a span inside one
  line and across wrapped lines, a whole element and a whole scene, typing
  before a span, an element inserted before, editing inside the quote,
  the quote deleted (to its element), the element deleted (to its scene),
  the script edited elsewhere (found again or unattached), a scene gone
  then its OMITTED heading, the `.fountain` never touched, flush, shot
  numbers never reused, renamed scenes, the anchor of a selection. The
  menus, painting and save checked through the real window (2026-10-30).
- `test_acts.py` — acts (story-structure/acts): the Act break is not in
  the PDF, the text after it moves up, the pagination still counts it,
  the screen page still shows it; `acts.actsOf` / `actAt` (no act break,
  scenes per act, scenes before the first act, empty name, empty act).
  The `ActPanel` itself needs a display and is not tested (checked by
  hand through the real window, 2026-10-26).
- `test_renderscreenplay.py` — PDF export with core fonts and with the
  custom TTF; an unusable custom font (not a font file, or no file) is an
  `error.MiscError`; non-Latin-1 widths in Helvetica; a printed PDF's
  `/OpenAction` goes to the cursor's page, an export has none.
- `test_manual.py` — `manual.build`: from `doc/` with the DocBook XSL
  stylesheets (skipped without `docbook-xsl`), a prebuilt page wins, a
  missing source is a `ManualError`.
- `test_myimport.py` — `importCeltx` (against `test.fountain` with the old
  ending) and `importTextFile` (against `test.fountain`); the real `wx`,
  with only `myimport.ImportDlg` patched to answer OK
  (`tests/test_myimport.py:40-42`).
- `test_pdfimport.py` — PDF import (`trelby/pdfimport.py`): draws its PDFs
  with ReportLab at test time (`makePdf`, US Letter, Courier 12; no PDF
  committed). With the profile `fixtures/pdf/letter-test.toml`: expected
  Fountain (written by `fountain.generate`) with accented names, the
  Fountain reading back to the same elements, page furniture dropped, dialogue joined
  across a page break, margin and typed scene numbers → `Line.num`
  written as `#n#`, dual
  dialogue → `^`, `strict` stops with page and line, lenient reading
  (nearest indent, columns as one line) with `IMPORT:` notes, a character
  with no speech → issue and note, profile errors, every profile in
  `trelby/pdfprofiles/` parses, the CLI with `--trace`. With the layout
  **detected**: the same script as with the profile, title page, page
  numbers, margin scene numbers, numbered heading without INT./EXT.,
  Trelby's own PDF export of `test.fountain` (detected = `trelby-a4.toml`),
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
- `test_fountain.py` — the native Fountain format (`trelby/fountain.py`):
  open → save → open byte-identical on `fixtures/fountain/*` (also with CRLF
  and a BOM, and without a final newline), every element type, title page
  read and edited, hidden source (boneyard, synopsis, `##`, `===`) kept,
  one edit rewrites one line, scene number and `^` kept on edit, insert and
  delete, forced `.` / `!` / `@` / `>` only when needed, lost elements
  reported, the shared fixture saved back unchanged, the old `test.trelby`
  ending reported lost. Loads the translations itself.
- `test_scenenumbers.py` — the numbering rule (fountain-native/scenes/1):
  `parse`/`fmt`/`key` order, a fresh script, append, inserts after a whole
  number and a letter, nesting, after `Z`, several in a row, no room,
  numbers never change, `check`; `1` before a first number above `1`
  (scenes/6).
- `test_scenes_model.py` — the scene number in the model and the file
  (fountain-native/scenes/2): `#n#` read into `Line.num`, round trip
  byte-identical, an edited heading keeps its number and spacing, a
  changed / added / removed number written, `str` / `fromStr`, wrapping,
  undo/redo of typing, join, split, type change, cut; cut and copy carry
  no number, a pasted scene has none, pasting at a heading's start,
  `report`, `deepcopy`.
- `test_scenes_finish.py` — the number given when a heading is finished
  (fountain-native/scenes/6, `scenenumbers.numberFinished`): none while
  typing (label `(3)`), Enter and moving away give it, an empty heading
  gets none, a pasted heading at once, an unnumbered script all at once,
  the cursor's heading skipped when some numbers exist, no room stays
  `?`, undo / redo, the save numbers the heading being typed.
- `test_scenes_save.py` — numbers given on save (fountain-native/scenes/3,
  `scenenumbers.prepareSave` / `renumberAll`): a new script `1..n`, no
  undo when nothing changes, append, insert, delete → `.OMITTED #n#` (and
  read back), a heading turned into Action, a scene made and removed
  between saves, cut and paste, copy, no room and duplicates stop the
  save, one undo step with `sceneNumbersIssued`, Renumber all and its
  undo, the cursor in a removed `OMITTED`.
- `test_scenes_screen.py` — scene numbers shown (fountain-native/scenes/4):
  `labels` / `labelAt` (`(1.A)` for a scene not numbered yet, `?` with no
  room), the PDF's numbers left and right of each heading and none when
  off, the screen page always numbered with `sceneLine` tags, the TOC, Go
  to scene's list, the scene report, the 5-click counter. The click and
  the dialogs need a display (checked through the real window on
  2026-10-27: numbers drawn at their headings in draft and layout, a click
  on each hits its heading, a click on the text does not, the save gives
  `2.A`; and on 2026-10-27 for scenes/6: an unnumbered script opened is
  numbered `1, 2`, a heading being typed shows `(3)` and gets `3` on
  Enter).
- `test_propwords.py` — `propwords.find_prop_words`: positions, accents,
  a multi-word run is one prop, punctuation ends a run, one-letter words
  inside a run but never at its ends, hyphen and apostrophe, mixed case and
  digits, an all-caps line, a run being typed not offered yet.
- `test_taborder.py` — `ConfigGlobal.tabOrder`: the default cycle and its
  wrap-around, elements outside the cycle, config round trip, `recalc`
  clean-up. Loads the translations itself.
- `test_keycode.py` — `util.eventKeyCode`: arrows and other non-character
  keys fall back to their `WXK_` code, characters keep their Unicode value,
  and the `util.MyKeyEvent` the insert commands send is read too.
- `test_opts.py` — `opts.init()`: `--conf <file>` and the scripts to open.
- `test_editorfixes.py` — End accepts a completion as one undo step;
  `Titles.sort` by y, then x; `MyCtrl.OnCopySystem` (fake control,
  clipboard patched) keeps the script's Action indent; the screen's
  CONTINUED number equals the PDF's on every page; side-by-side scrolling
  by direction.
- `test_i18n.py` — static checks over `trelby/`: no `_()` around an
  already formatted string, and no translated string as a `setattr` name,
  a `Vars.add*` name or save name, or a helper argument that becomes one.
- `test_importfountain.py` — `MyCtrl.importFile` on a fake control: a
  `.fountain` (any case) is read by `readFountain` like Open and the tab
  stays untitled and modified; an unreadable one changes nothing; other
  formats are picked by their extension in any case.
- `test_openfilms.py` — bugs/editor/20: two films open, each script
  finds its own film, a root opened again replaced; tab switches (fake
  frame) show each tab's film, bible and annotations, and a script of no
  film none; a save of a tab that is not the current one renames its own
  film's records only. The real window checked with copies of two films
  (2026-10-31).
- `test_saveall.py` — `MyFrame.saveAll` on fake tabs: every modified tab
  is saved, and one left unsaved (Save As cancelled) calls the exit off.
- `test_wxnames.py` — every `wx.<name>` used in `trelby/` exists in the
  installed wxPython (names removed in wxPython 4 fail only when their
  dialog opens, bugs/editor/17); submodules and prefixes are exceptions,
  and so would be an open bug's name (`KNOWN`, empty now).
- `test_util.py` — `util.replace`, `splitToWords`, `escapeStrings`,
  `loadLatin1EncodedFile`, `getPDFViewer` on Linux (xdg-open, else evince); the file
  itself is ISO-8859-1 encoded.
- `execute_random_tests.py` — manual fuzzer: random command sequences on a
  `Screenplay`, saving failing sequences (and the script as `.fountain`)
  in the current directory (`# ut:ignore`, not collected by pytest because
  of its name). Run from the repository root:
  `python -m tests.execute_random_tests [file.ops]`; it prints only on a
  failure (checked to start and run, 2026-10-27).

## Key facts / gotchas
- Every test runs with the real `wx` and no display: nothing replaces
  `sys.modules["wx"]` and nothing sets `TRELBY_TESTING`
  (`trelby/config.py:14`); a test that would open a dialog patches that
  dialog. Several test files still load the translations themselves, which
  `tests/u.py` already does.
- PDFs are generated, not committed: Rafael's real PDFs hold film text and
  stay out of the repo (decided in the pdf-import initiative, task
  importer/1, now in git history).
- Not covered by any test: the wx GUI (`trelbyframe`, `trelbyctrl`,
  `viewmode`, dialogs; the Fountain open/save in `MyCtrl` was checked by
  hand through the real window, 2026-10-24 and 2026-10-25),
  FDX/HTML/RTF/text export, FDX/Astx/Fade In import (Fountain is one
  reader and writer for open, save, import and export: `test_fountain.py`,
  `test_importfountain.py`), pagination results,
  undo/redo.
- Every run shows about 77 `DeprecationWarning`s for `wx.NewId()` from
  `trelby/ids.py`, imported through `trelbyframe` by `test_saveall.py`;
  harmless, the ids still work.

## Touchpoints
- Tests: `trelby/scenenumbers.py`, `trelby/screenplay.py`, `trelby/config.py`, `trelby/myimport.py`,
  `trelby/pdfimport.py`, `trelby/fountain.py`, `trelby/pdf.py`,
  the report modules, `trelby/locations.py`, `trelby/pagelist.py`,
  `trelby/util.py`.
- Run by: `docker/test.sh`, `.github/workflows/main.yml`.
