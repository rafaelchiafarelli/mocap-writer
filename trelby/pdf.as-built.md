# pdf.py — as built

`trelby/pdf.py` (362 lines) writes a PML document (`trelby/pml.py`) as a PDF
with ReportLab. It is the only PDF writer: script export, print, reports,
watermarks, the dialogue chart and script comparison all build PML and call
`pdf.generate`. It does not read PDFs.

## Entry point

- `generate(doc: pml.Document) -> bytes` (`trelby/pdf.py:20`) →
  `PDFExporter(doc).generate()` (`trelby/pdf.py:250`).

## How a document is drawn

- One ReportLab `Canvas` sized `doc.w × doc.h` mm converted to points,
  PDF 1.5, creator/producer `Trelby <version>`, `doc.uniqueId` as keywords
  (watermarks) (`trelby/pdf.py:252-264`).
- For each `pml.Page`, each op is drawn by its class's `pdfOp`
  (`trelby/pdf.py:274-280`), a `PDFDrawOp` singleton set on the PML class
  (`trelby/pml.py:122`, `trelby/pml.py:175`, `trelby/pml.py:193`,
  `trelby/pml.py:216`, `trelby/pml.py:239`):
  - `PDFTextOp` (`trelby/pdf.py:36`): PML y is the top of the text, PDF y is
    the baseline, so `y - 0.843 * size` (`trelby/pdf.py:53-54`);
    `drawString`, or for `angle` 45/90 a literal `BT … Tm … Tj ET` block
    (`trelby/pdf.py:59-80`); underline drawn as a line 0.1 × size below the
    baseline; a `toc` item adds a bookmark and an outline entry
    (`trelby/pdf.py:96-101`).
  - `PDFLineOp` (`trelby/pdf.py:104`), `PDFRectOp` (`trelby/pdf.py:132`),
    `PDFQuarterCircleOp` (Bézier quarter circle, `trelby/pdf.py:153`),
    `PDFArbitraryOp` (raw PDF operators from `pml.PDFOp`,
    `trelby/pdf.py:187`).
- The outline (TOC) is shown on open when `doc.showTOC`
  (`trelby/pdf.py:282-283`).
- Coordinates: `mm2points` = mm × 2.83464567; `x(mm)`, `y(mm)` flips the
  vertical axis (`trelby/pdf.py:345-362`).

## Fonts

- `PDFExporter.fonts` maps PML style bits (font family | bold | italic) to
  the 12 PDF core fonts: Courier, Helvetica, Times-Roman families
  (`trelby/pdf.py:234-247`).
- `getFontForFlags(flags)` (`trelby/pdf.py:312`): if the script configured a
  custom font for that style (`doc.fonts`, filled from `Config.pdfFonts` by
  `Screenplay.generatePML`, `trelby/screenplay.py:873-877`), registers the
  TTF with ReportLab once and returns its name; otherwise the core font.
  The underline bit is masked with `& 15`.
- Screen layout and PDF use the same text widths: `fontinfo` gives core-font
  metrics in mm (`trelby/util.py:515-516`), and script text is always
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

- `import trelby.pml as util` (`trelby/pdf.py:9`): `util` in this module is
  `pml`, not `trelby.util`; nothing uses it.
- `doc.defPage` ("open PDF on current page", set by
  `Screenplay.generatePML`, `trelby/screenplay.py:862-863`) is ignored: the
  `/OpenAction` code is commented out (`trelby/pdf.py:266-269`). The
  `pdfOpenOnCurrentPage` setting therefore has no effect.
- Rotated text (watermarks) goes through `addLiteral` with
  `escapeStr`, so only characters ReportLab's literal path can encode come
  out right (comment at `trelby/pdf.py:77`).
- Left-overs from the pre-ReportLab writer: `FontInfo.number` / `pdfObj`,
  `PDFObject`, `genStream` (with a Python 2 `s.encode("zlib")`)
  (`trelby/pdf.py:199-309`) are not used by `generate`.
- `PDFLineOp` with fewer than two points prints a message to stdout and
  draws nothing (`trelby/pdf.py:115-118`).
- An unknown custom font name with no file raises a plain `Exception`
  (`trelby/pdf.py:325-333`); callers do not catch it.
- Text widths for Helvetica/Times use 256-entry tables; a character above
  U+00FF in a title string raises `IndexError` in `fontinfo`
  (`trelby/fontinfo.py:57-60`), before this module is reached.

## Tests

- `tests/test_renderscreenplay.py`: `generatePDF` on
  `tests/fixtures/test.trelby` with core fonts and with the custom TTF in
  `tests/fixtures/custom-font/` (checks only the `%PDF-1.5` header and
  size).
- Indirectly: `tests/test_scriptreport.py`, `tests/test_scenereport.py`,
  `tests/test_locationreport.py`, `tests/test_characterreport.py` (report
  PDFs).
- Not covered: rotated text, TOC, line/rect/circle ops, page content.
