## 1. PDF importer

- **Status:** Implemented, in live test (2026-10-24) — not done.
  Delivered: `trelby/pdfimport.py` (layout detection, classification,
  `IMPORT:` notes, report, `probe`, CLI, trace, optional profiles), File →
  Import `.pdf` with no question and an import report
  (`myimport.importPdf`), `docker/pdfimport.sh`, instrumented trace
  (`--trace`; `MOCAP_WRITER_PDF_TRACE` in the GUI),
  `tests/test_pdfimport.py`. On Rafael's four PDFs (two Letter / Courier
  Prime, two A4 landscape printed from Word or Docs) the detected layout
  gives the same script as hand-written profiles. **Open:** Rafael's test
  of File → Import in the editor; the task is done when he accepts it.
- **Decision (Rafael, 2026-10-24): no profile choice.** "I want to click the
  import button and the program would import", with the problems reported
  in a warning page or as notes in the file saying what is wrong and how to
  fix it. This replaces the original contract's explicit layout profile
  ("never guessed") and its stop on an unknown indent; the layout is now
  detected from the PDF, still deterministically and with no LLM.
- **Type:** code
- **Depends on:** `pdfplumber` (MIT; its deps pdfminer.six MIT, pypdfium2
  Apache-2.0/BSD-3) in `docker/requirements.in` and the hashed lockfile. Not
  PyMuPDF (AGPL)
- **Contract** (as revised by the decision above):
  - In: a screenplay PDF with selectable text, master-scene format; nothing
    else
  - Requires: deterministic classification by each line's position, **no
    LLM**; the layout (scene/action, character, parenthetical, dialogue and
    transition indents, page numbers, title page, margin or typed scene
    numbers, dual dialogue) detected from the PDF's own statistics; page
    furniture (`(MORE)`, `(CONT'D)`, `CONTINUED`, page numbers) dropped;
    dialogue that continues across a page break joined; dual dialogue →
    Fountain `^`; scene numbers → `#n#`; reuses the editor's element types
    (`screenplay.Line`). The import never stops on a doubtful line: it is
    read as well as possible and reported
  - Delivers:
    - File → Import accepts `.pdf`, asks nothing, and shows an import
      report (layout found, every issue)
    - every issue also as an `IMPORT: … (PDF page p, line l)` Note element
      just before the text it is about, saying what to fix
    - CLI `python -m trelby.pdfimport import <pdf>... --out <dir>` writing
      one `.fountain` per PDF through `Screenplay.generateFountain`, notes
      as `[[IMPORT: …]]`; `--profile` / `--strict` for the old explicit mode
    - `probe` subcommand: the indents found and the layout detected
- **Pre-work:**
  - Done (2026-10-24): `pdfplumber` 0.11.10 in `docker/requirements.in`
    and the lockfile (`fixes/000067/pdfplumber-dependency`)
  - ~~Neutral hand-made PDF fixtures, one per source program, committed
    under `tests/fixtures/pdf/`~~ **Replaced (Rafael, 2026-10-24):** the
    tests draw their PDFs with ReportLab at test time and round-trip
    Trelby's own PDF export; Rafael's real scripts are the live check. They
    hold film text, so they are **never committed**
- **Out of scope:** OCR; importing the film's own PDFs into its film root (a
  film session does that)
- **Tests:** generated PDFs → expected `.fountain`, with a profile and
  detected (same result); accented character names; dual dialogue; page
  furniture dropped; dialogue across a page break; title page; scene
  numbers; issues and notes; `strict` stops with page and line; `probe`
