# pdf.py — as built

`trelby/pdf.py` (362 lines) writes a PML document (`trelby/pml.py`) as a PDF
with ReportLab. It is the only PDF writer: script export, print, reports,
watermarks, the dialogue chart and script comparison all build PML and call
`pdf.generate`. It does not read PDFs.

## Entry point

- `generate(doc: pml.Document) -> bytes` (`trelby/pdf.py:22`) →
  `PDFExporter(doc).generate()` (`trelby/pdf.py:252`).

## How a document is drawn

- One ReportLab `Canvas` sized `doc.w × doc.h` mm converted to points,
  PDF 1.5, creator/producer `Trelby <version>`, `doc.uniqueId` as keywords
  (watermarks) (`trelby/pdf.py:254-266`).
- For each `pml.Page`, each op is drawn by its class's `pdfOp`
  (`trelby/pdf.py:276-282`), a `PDFDrawOp` singleton set on the PML class
  (`trelby/pml.py:122`, `trelby/pml.py:175`, `trelby/pml.py:193`,
  `trelby/pml.py:216`, `trelby/pml.py:239`):
  - `PDFTextOp` (`trelby/pdf.py:38`): PML y is the top of the text, PDF y is
    the baseline, so `y - 0.843 * size` (`trelby/pdf.py:55-56`);
    `drawString`, or for `angle` 45/90 a literal `BT … Tm … Tj ET` block
    (`trelby/pdf.py:61-82`); underline drawn as a line 0.1 × size below the
    baseline; a `toc` item adds a bookmark and an outline entry
    (`trelby/pdf.py:98-103`).
  - `PDFLineOp` (`trelby/pdf.py:106`), `PDFRectOp` (`trelby/pdf.py:134`),
    `PDFQuarterCircleOp` (Bézier quarter circle, `trelby/pdf.py:155`),
    `PDFArbitraryOp` (raw PDF operators from `pml.PDFOp`,
    `trelby/pdf.py:189`).
- The outline (TOC) is shown on open when `doc.showTOC`
  (`trelby/pdf.py:284-285`).
- Coordinates: `mm2points` = mm × 2.83464567; `x(mm)`, `y(mm)` flips the
  vertical axis (`trelby/pdf.py:354-371`).

## Fonts

- `PDFExporter.fonts` maps PML style bits (font family | bold | italic) to
  the 12 PDF core fonts: Courier, Helvetica, Times-Roman families
  (`trelby/pdf.py:236-249`).
- `getFontForFlags(flags)` (`trelby/pdf.py:314`): if the script configured a
  custom font for that style (`doc.fonts`, filled from `Config.pdfFonts` by
  `Screenplay.generatePML`, `trelby/screenplay.py:520-524`), registers the
  TTF with ReportLab once and returns its name; otherwise the core font.
  The underline bit is masked with `& 15`.
- Screen layout and PDF use the same text widths: `fontinfo` gives core-font
  metrics in mm (`trelby/util.py:528-529`), and script text is always
  Courier, 0.6 × size per character.

## Extension points

- **New drawing primitive**: a PML op class with a `pdfOp` and a matching
  `PDFDrawOp` subclass here.
- **Custom fonts**: per script in Settings → PDF/Fonts
  (`trelby/configpages/pdffontspanel.py:9`), saved as `Font/<style>/Name`
  and `Font/<style>/Filename` in the script config.
- **PDF import** (a planned initiative) has nothing to build on here: this
  module only writes.

## Gotchas

- `import trelby.pml as util` (`trelby/pdf.py:11`): `util` in this module is
  `pml`, not `trelby.util`; nothing uses it.
- `doc.defPage` ("open PDF on current page", set by
  `Screenplay.generatePML`, `trelby/screenplay.py:509-510`) is ignored: the
  `/OpenAction` code is commented out (`trelby/pdf.py:268-271`). The
  `pdfOpenOnCurrentPage` setting therefore has no effect. Bug: [bugs/import-export/9](../initiatives/bugs/epics/import-export/tasks/9-pdf-open-on-page.md).
- Rotated text (watermarks) goes through `addLiteral` with
  `escapeStr`, so only characters ReportLab's literal path can encode come
  out right (comment at `trelby/pdf.py:79`). Bug: [bugs/import-export/8](../initiatives/bugs/epics/import-export/tasks/8-watermark-non-latin.md).
- Left-overs from the pre-ReportLab writer: `FontInfo.number` / `pdfObj`,
  `PDFObject`, `genStream` (with a Python 2 `s.encode("zlib")`)
  (`trelby/pdf.py:201-311`) are not used by `generate`.
- `PDFLineOp` with fewer than two points prints a message to stdout and
  draws nothing (`trelby/pdf.py:117-120`).
- A custom font that cannot be used (a name with no file, or a file
  ReportLab cannot read) raises `error.MiscError` (`trelby/pdf.py:327-346`);
  Export, Print (`MyCtrl.makePDF`, `trelby/trelbyctrl.py:1216`) and
  Watermark show it in a message box. The script settings only send a
  font that has a file (`trelby/screenplay.py:520-524`).
- Text widths for Helvetica/Times use Latin-1 tables; a character above
  U+00FF is measured like `?` (`trelby/fontinfo.py:50-65`); the core fonts
  cannot draw it.

## Tests

- `tests/test_renderscreenplay.py`: `generatePDF` on
  `tests/fixtures/test.fountain` with core fonts and with the custom TTF in
  `tests/fixtures/custom-font/` (checks only the `%PDF-1.5` header and
  size).
- Indirectly: `tests/test_scriptreport.py`, `tests/test_scenereport.py`,
  `tests/test_locationreport.py`, `tests/test_characterreport.py` (report
  PDFs).
- Not covered: rotated text, TOC, line/rect/circle ops, page content.
