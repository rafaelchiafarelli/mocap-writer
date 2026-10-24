# pdfimport.py — as built

`trelby/pdfimport.py` turns a master-scene screenplay PDF with selectable
text into a list of `Line`s, classifying each line by its horizontal
position as declared in a layout profile (`pdfprofiles/CLAUDE.md`). No wx
at import time and no LLM; `pdfplumber` is imported only when a PDF is read
(`trelby/pdfimport.py:231`). The GUI wrapper is `myimport.importPdf`
(`trelby/myimport.py:768`).

## Contract

- In: a PDF path and a `Profile` (`loadProfile`, `trelby/pdfimport.py:115`);
  optional `trace` and `warnings` lists and `skipPages` (default: the
  profile's).
- Out: `importPdf` (`trelby/pdfimport.py:587`) returns `list[Line]` meeting
  the importer contract of `myimport.as-built.md`: every line `LB_SPACE`,
  the last line of each element `LB_LAST`, so the caller's `reformatAll`
  re-wraps them, as `importTextFile` does.
- Errors: `PdfImportError` with `.page` / `.lineNo` (1-based; `lineNo`
  counts every text line of the page, furniture included)
  (`trelby/pdfimport.py:40`): unknown indent (`trelby/pdfimport.py:443`),
  more than two columns (`trelby/pdfimport.py:400`), two columns that do not
  start with two character names, a dual-column piece matching no column
  rule, no text at all (`trelby/pdfimport.py:611`), and every profile
  error.

## Stages

1. **Extract** (`extractPages`, `trelby/pdfimport.py:230`): pdfplumber
   words per page, sorted by top then x; words whose top is within 2 pt of
   the line's first word form one line (`trelby/pdfimport.py:247`).
2. **Per line** (`_items`, `trelby/pdfimport.py:348`), pages up to
   `skipPages` skipped (`trelby/pdfimport.py:355`):
   1. the whole line text matched against the `[[drop]]` rules → dropped
      (`trelby/pdfimport.py:369`);
   2. words matching `[scene_numbers]` at its `left`/`right` positions are
      removed and kept as the line's scene number
      (`trelby/pdfimport.py:377-387`);
   3. split into segments at gaps wider than `segment_gap` (`_split`,
      `trelby/pdfimport.py:260`);
   4. two segments start a **dual-dialogue block** if they classify as
      character by `dual.left` / `dual.right` (`trelby/pdfimport.py:409`);
      inside the block every segment, even a lone one, is classified by
      the column rules; the block ends at a vertical gap above
      `paragraph_gap` or at a page end;
   5. otherwise one segment classified by `[[indent]]` (`_classify`,
      `trelby/pdfimport.py:330`), first match wins; `scene_action` checks
      `scene_prefixes`, also after cutting an `[scene_numbers] inline`
      number (`_inlineNumber`, `trelby/pdfimport.py:311`; a `scene` rule
      cuts it without the prefix check); a scene heading gets ` #n#`
      appended, the margin number winning over the inline one
      (`trelby/pdfimport.py:452-454`).
3. **Elements** (`_elements`, `trelby/pdfimport.py:475`): a new element
   starts on a type change, a column/block change, every character and
   transition line, a parenthetical line starting with `(`, a vertical gap
   above `paragraph_gap`, or a new page unless the line is dialogue
   (`startsNew`, `trelby/pdfimport.py:483-494`). Character names lose their
   `character_suffix` matches; a character at the top of a page that repeats
   the speaker of the dialogue/parenthetical that ended the previous page is
   dropped, so the speech goes on (`trelby/pdfimport.py:504-511`). Each
   dual-dialogue column continues from its own previous item
   (`prevByColumn`, `trelby/pdfimport.py:481`); the right column's character
   gets ` ^` (`trelby/pdfimport.py:537`) and its elements are moved after
   the left column's (`trelby/pdfimport.py:545`).
4. **Warnings** (`_warnings`, `trelby/pdfimport.py:568`): a character
   element not followed by a parenthetical or dialogue — usually a speech
   typed at the action indent in the source — is reported as
   `(page, lineNo, message)` in `importPdf`'s `warnings` list and as a
   `WARNING` row at the end of the trace. The import goes on.
5. **Out**: `importPdf` builds the `Line`s. `toScreenplay`
   (`trelby/pdfimport.py:663`) wraps them in a `Screenplay` with **no title
   pages** (`trelby/pdfimport.py:673`), reformatted and paginated, for
   `generateFountain`.

## Other entry points

- `probe(path, skipPages, segmentGap)` (`trelby/pdfimport.py:617`): one row
  per (x0, column) with count, right-edge range and three sample lines, for
  writing a profile.
- `writeTrace(trace, path)` (`trelby/pdfimport.py:653`): the trace as TSV,
  columns `page line top x0 x1 decision rule text`. Decisions: an element
  name, `dual left|right <element>`, `dropped`, `scene number`,
  `skipped page`, `UNKNOWN INDENT` (the last row before an error),
  `WARNING` (see stage 4).
- `main(argv)` (`trelby/pdfimport.py:680`), `python -m trelby.pdfimport`:
  `import <pdf>... --profile <toml> --out <dir> [--skip-pages N] [--trace]`
  writes `<name>.fountain` (and `<name>.trace.tsv`, also when the import
  stops), prints each warning with its page and line
  (`trelby/pdfimport.py:737`) and the element counts; exit 1 if any PDF
  failed.
  `probe <pdf> [--skip-pages N] [--segment-gap G]`.

## Gotchas

- **Action cut by a page break becomes two paragraphs:** only dialogue
  continues across pages (`trelby/pdfimport.py:492-494`).
- Lines are rejoined with single spaces: multiple spaces collapse, a word
  cut over two lines gets a space inside it, and a hyphen at a line end
  stays (`bem- vindo`).
- A scene heading whose text has no `scene_prefixes` entry comes back as
  Action under a `scene_action` rule (same limit as `importTextFile`).
- Trelby has no dual-dialogue or scene-number fields: `^` and `#n#` stay in
  the element text in the editor; in the Fountain export they are valid
  Fountain markup.
- Fixed 2 pt tolerance for grouping words into a line
  (`trelby/pdfimport.py:247`), not a profile key.
- An action line with a gap wider than `segment_gap` (e.g. aligned text in
  a table) is read as two columns and stops the import.
- Warnings reach the GUI only through the trace summary
  (`$MOCAP_WRITER_PDF_TRACE`); without it they are not shown.
- The title page is not imported (use `skip_pages`); the CLI output has no
  Fountain title block.

## Tests

`tests/test_pdfimport.py` draws its PDFs with ReportLab at test time
(profile `tests/fixtures/pdf/letter-test.toml`) and round-trips Trelby's own
PDF export of `test.trelby` through `trelby-a4.toml`.
