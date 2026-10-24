# pdfimport.py — as built

`trelby/pdfimport.py` turns a master-scene screenplay PDF with selectable
text into a list of `Line`s, classifying each line by its horizontal
position as declared in a layout profile (`pdfprofiles/CLAUDE.md`). No wx
at import time and no LLM; `pdfplumber` is imported only when a PDF is read
(`trelby/pdfimport.py:229`). The GUI wrapper is `myimport.importPdf`
(`trelby/myimport.py:768`).

## Contract

- In: a PDF path and a `Profile` (`loadProfile`, `trelby/pdfimport.py:114`);
  optional `trace` list and `skipPages` (default: the profile's).
- Out: `importPdf` (`trelby/pdfimport.py:538`) returns `list[Line]` meeting
  the importer contract of `myimport.as-built.md`: every line `LB_SPACE`,
  the last line of each element `LB_LAST`, so the caller's `reformatAll`
  re-wraps them, as `importTextFile` does.
- Errors: `PdfImportError` with `.page` / `.lineNo` (1-based; `lineNo`
  counts every text line of the page, furniture included)
  (`trelby/pdfimport.py:40`): unknown indent (`trelby/pdfimport.py:413`),
  more than two columns (`trelby/pdfimport.py:370`), two columns that do not
  start with two character names, a dual-column piece matching no column
  rule, no text at all (`trelby/pdfimport.py:552`), and every profile
  error.

## Stages

1. **Extract** (`extractPages`, `trelby/pdfimport.py:228`): pdfplumber
   words per page, sorted by top then x; words whose top is within 2 pt of
   the line's first word form one line (`trelby/pdfimport.py:245`).
2. **Per line** (`_items`, `trelby/pdfimport.py:318`), pages up to
   `skipPages` skipped (`trelby/pdfimport.py:325`):
   1. the whole line text matched against the `[[drop]]` rules → dropped
      (`trelby/pdfimport.py:339`);
   2. words matching `[scene_numbers]` at its `left`/`right` positions are
      removed and kept as the line's scene number
      (`trelby/pdfimport.py:347-357`);
   3. split into segments at gaps wider than `segment_gap` (`_split`,
      `trelby/pdfimport.py:258`);
   4. two segments start a **dual-dialogue block** if they classify as
      character by `dual.left` / `dual.right` (`trelby/pdfimport.py:379`);
      inside the block every segment, even a lone one, is classified by
      the column rules; the block ends at a vertical gap above
      `paragraph_gap` or at a page end;
   5. otherwise one segment classified by `[[indent]]` (`_classify`,
      `trelby/pdfimport.py:304`), first match wins; `scene_action` checks
      `scene_prefixes`; a scene heading gets ` #n#` appended
      (`trelby/pdfimport.py:423-424`).
3. **Elements** (`_elements`, `trelby/pdfimport.py:445`): a new element
   starts on a type change, a column/block change, every character and
   transition line, a parenthetical line starting with `(`, a vertical gap
   above `paragraph_gap`, or a new page unless the line is dialogue
   (`startsNew`, `trelby/pdfimport.py:453-464`). Character names lose their
   `character_suffix` matches; a character at the top of a page that repeats
   the speaker of the dialogue/parenthetical that ended the previous page is
   dropped, so the speech goes on (`trelby/pdfimport.py:474-481`). Each
   dual-dialogue column continues from its own previous item
   (`prevByColumn`, `trelby/pdfimport.py:451`); the right column's character
   gets ` ^` (`trelby/pdfimport.py:507`) and its elements are moved after
   the left column's (`trelby/pdfimport.py:515`).
4. **Out**: `importPdf` builds the `Line`s. `toScreenplay`
   (`trelby/pdfimport.py:604`) wraps them in a `Screenplay` with **no title
   pages** (`trelby/pdfimport.py:614`), reformatted and paginated, for
   `generateFountain`.

## Other entry points

- `probe(path, skipPages, segmentGap)` (`trelby/pdfimport.py:558`): one row
  per (x0, column) with count, right-edge range and three sample lines, for
  writing a profile.
- `writeTrace(trace, path)` (`trelby/pdfimport.py:594`): the trace as TSV,
  columns `page line top x0 x1 decision rule text`. Decisions: an element
  name, `dual left|right <element>`, `dropped`, `scene number`,
  `skipped page`, `UNKNOWN INDENT` (the last row before an error).
- `main(argv)` (`trelby/pdfimport.py:621`), `python -m trelby.pdfimport`:
  `import <pdf>... --profile <toml> --out <dir> [--skip-pages N] [--trace]`
  writes `<name>.fountain` (and `<name>.trace.tsv`, also when the import
  stops) and prints the element counts; exit 1 if any PDF failed.
  `probe <pdf> [--skip-pages N] [--segment-gap G]`.

## Gotchas

- **Action cut by a page break becomes two paragraphs:** only dialogue
  continues across pages (`trelby/pdfimport.py:462-464`).
- Lines are rejoined with single spaces: multiple spaces collapse, a word
  cut over two lines gets a space inside it, and a hyphen at a line end
  stays (`bem- vindo`).
- A scene heading whose text has no `scene_prefixes` entry comes back as
  Action under a `scene_action` rule (same limit as `importTextFile`).
- Trelby has no dual-dialogue or scene-number fields: `^` and `#n#` stay in
  the element text in the editor; in the Fountain export they are valid
  Fountain markup.
- Fixed 2 pt tolerance for grouping words into a line
  (`trelby/pdfimport.py:245`), not a profile key.
- An action line with a gap wider than `segment_gap` (e.g. aligned text in
  a table) is read as two columns and stops the import.
- The title page is not imported (use `skip_pages`); the CLI output has no
  Fountain title block.

## Tests

`tests/test_pdfimport.py` draws its PDFs with ReportLab at test time
(profile `tests/fixtures/pdf/letter-test.toml`) and round-trips Trelby's own
PDF export of `test.trelby` through `trelby-a4.toml`.
