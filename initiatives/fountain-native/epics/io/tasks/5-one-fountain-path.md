## 5. One Fountain reader and writer

- **Status:** Done (2026-10-26) — Rafael approved the plan and kept Import →
  Fountain, through `fountain.load`; the old importer's options are a future
  feature (`../../import/tasks/1-fountain-import-options.md`). Export →
  Fountain and the PDF command line write with `fountain.generate`;
  `generateFountain` and `importFountain` deleted. 166 tests (3 new:
  `testFountainReadsBack`, `tests/test_importfountain.py`, which checks
  the import's routing on a fake control rather than comparing with Open:
  both go through `MyCtrl.readFountain`, and a real `MyCtrl` needs a
  window); six
  `test_pdfimport.py` expected texts gained the final newline
  `fountain.generate` writes, nothing else changed in them.
- **Why:** Open and Save use `fountain.load` / `fountain.generate`, but three
  paths still use upstream's one-way Fountain code: Export → Fountain
  (`Screenplay.generateFountain`, `trelby/trelbyctrl.py:1183`), the PDF
  import command line (`trelby/pdfimport.py:1151`, how existing PDF scripts
  become Fountain) and Import → Fountain (`myimport.importFountain`,
  `trelby/trelbyctrl.py:220`). That code carries five open bugs:
  import-export/1, 2 (import crashes), 4 (Action starting `INT`/`EXT`
  written with trailing spaces), 5 (`[A-za-z]` title pattern) and 6 (empty
  title string crashes the export). Sending every path through `fountain`
  closes them by removal instead of patching code that will be deleted.

- **Type:** code
- **Depends on:** io/1 (`fountain.load` / `generate`)
- **Contract:**
  - In: `Screenplay.generateFountain`, `myimport.importFountain` and its
    callers above; `tests/test_pdfimport.py:61`, which writes its expected
    output with `generateFountain`
  - Requires:
    - Export → Fountain writes `fountain.generate(sp).text`, and shows
      `res.lost` the way Save does (`MyCtrl.showLost`).
    - `python -m trelby.pdfimport import` writes `fountain.generate(sp).text`
      and prints `res.lost` to stderr, one line per element.
    - Import of a `.fountain` builds the script with `fountain.load`, like
      Open, but the tab stays untitled (Save asks for a name), as every
      import does today.
    - `Screenplay.generateFountain`, `myimport.importFountain` and the
      Fountain branch of its option dialog are deleted.
  - Delivers: one Fountain reader and one writer in the program; bugs
    import-export/1, 2, 4, 5, 6 marked fixed by this task.
- **Pre-work:** —
- **Out of scope:** the other importers and exporters; import-export/3
  (extension matching) stays a bug; the GUI PDF import, which hands lines
  to the editor and does not write Fountain.
- **Tests:** the full suite. `test_pdfimport.py` expected texts may change
  where the two writers differ (e.g. trailing spaces); each change
  explained in the commit. New: a PDF import's Fountain reads back through
  `fountain.load` to the same element types and texts; importing
  `tests/fixtures/fountain/elements.fountain` gives the same lines as
  opening it.
- **Decisions:** plan approved; Import → Fountain kept as a way in, and
  its old options planned as a feature for later (Rafael, 2026-10-26).
