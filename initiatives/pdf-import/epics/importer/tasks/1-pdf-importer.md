## 1. PDF importer

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
- **Pre-work:** **neutral** PDF fixtures, one per source program (Final Draft,
  Celtx, Word, Google Docs), made by hand by Rafael: the text of
  `mocap-previz/docs/exploration/script-to-previz/spikes/fountain/sample_ptbr.fountain`
  typed in each program and exported to PDF (no film text), committed under
  `tests/fixtures/pdf/`
- **Out of scope:** OCR; writing profiles for the film's own PDFs and importing
  them (a film session does that with `probe` and the CLI on the film root)
- **Tests:** each fixture → expected `.fountain`; unknown indent stops with
  page and line; accented character names; dual dialogue; page furniture
  dropped; dialogue across a page break; `probe` output on a fixture
