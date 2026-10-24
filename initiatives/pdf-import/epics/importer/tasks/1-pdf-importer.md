## 1. PDF importer

- **Status:** Implemented, in live test (2026-10-24) — not done.
  Delivered: `trelby/pdfimport.py` (profile format, classification, `probe`,
  CLI, trace), File → Import `.pdf` (`myimport.importPdf`), starter profile
  `trelby/pdfprofiles/trelby-a4.toml`, `docker/pdfimport.sh`, instrumented
  trace (`--trace`; `MOCAP_WRITER_PDF_TRACE` in the GUI),
  `tests/test_pdfimport.py`. **Open:** one starter profile per source
  program (Final Draft, Celtx, Word, Google Docs), built with `probe` from
  real PDFs in the live test with Rafael; the task is done when those
  profiles are committed and his PDFs import with no unknown-indent stop.
- **Type:** code
- **Depends on:** `pdfplumber` (MIT; its deps pdfminer.six MIT, pypdfium2
  Apache-2.0/BSD-3) in `docker/requirements.in` and the hashed lockfile. Not
  PyMuPDF (AGPL)
- **Contract:**
  - In: a screenplay PDF with selectable text, master-scene format, and a
    **layout profile** chosen explicitly (never guessed)
  - Requires: deterministic classification by each line's left indent (x
    position, in points), **no LLM**; the profile is a file declaring indent
    ranges → element (scene heading, action, character, parenthetical,
    dialogue, transition) and page-furniture rules (page numbers, `(MORE)`,
    `(CONT'D)`, `CONTINUED`, headers/footers) to drop; a line whose indent
    matches no range stops the import with its page and line; margin scene
    numbers become `#n#`; dialogue that continues across a page break is
    joined; dual dialogue (two columns) becomes Fountain `^`; reuses the
    editor's element types (`screenplay.Line`), so the result is what
    `importTextFile` would produce for the same lines
  - Delivers:
    - File → Import accepts `.pdf` (asks for the profile)
    - CLI `python -m trelby.pdfimport <pdf>... --profile <file> --out <dir>`
      writing one `.fountain` per PDF through `Screenplay.generateFountain`
    - `probe` subcommand: the indents found in a PDF with counts and sample
      lines, so a film session can write a profile
    - the profile format, and one starter profile per source program built
      from the fixtures
- **Pre-work:**
  - Done (2026-10-24): `pdfplumber` 0.11.10 in `docker/requirements.in`
    and the lockfile (`fixes/000067/pdfplumber-dependency`)
  - ~~Neutral hand-made PDF fixtures, one per source program, committed
    under `tests/fixtures/pdf/`~~ **Replaced (Rafael, 2026-10-24):** the
    tests draw their PDFs with ReportLab at test time (a Final Draft-like
    layout, `tests/fixtures/pdf/letter-test.toml`) and round-trip Trelby's
    own PDF export; Rafael's real scripts are the check for the
    per-program profiles. They hold film text, so they are **never
    committed**: they stay where they are and only the profiles (layout
    positions, no text) come into the repo
- **Out of scope:** OCR; writing profiles for the film's own PDFs and importing
  them (a film session does that with `probe` and the CLI on the film root)
- **Tests:** each generated PDF → expected `.fountain`; unknown indent stops with
  page and line; accented character names; dual dialogue; page furniture
  dropped; dialogue across a page break; `probe` output on a fixture
