# pdfimport.py — as built

`trelby/pdfimport.py` turns a master-scene screenplay PDF with selectable
text into a list of `Line`s, classifying each line by its horizontal
position. The layout is **detected from the PDF itself** (`detectLayout`);
a TOML layout profile (`pdfprofiles/CLAUDE.md`) can be given instead, from
the command line only. Deterministic, no LLM, no wx at import time;
`pdfplumber` is imported only when a PDF is read
(`trelby/pdfimport.py:282`). The GUI wrapper is `myimport.importPdf`
(`trelby/myimport.py:769`).

**Nothing stops the import** (Rafael, 2026-10-24): anything doubtful is read
as well as possible and becomes an `Issue` (page, line, message) and, by
default, an `IMPORT: … (PDF page p, line l)` **Note element just before the
element it is about**, saying what is wrong and how to fix it. `strict=True`
(CLI `--strict`) restores the old behaviour of stopping at the first line no
rule covers.

## Contract

- In: a PDF path; optional `profile` (`None` = detect), `trace`, `issues`
  and `layout` lists, `skipPages` (default: detected / the profile's),
  `notes` (default on), `strict` (default off) — `importPdf`
  (`trelby/pdfimport.py:921`).
- Out: `list[Line]` meeting the importer contract of `myimport.as-built.md`:
  every line `LB_SPACE`, the last line of each element `LB_LAST`, notes as
  one-line `NOTE` elements, so the caller's `reformatAll` re-wraps them.
- Errors (`PdfImportError`, `.page` / `.lineNo`,
  `trelby/pdfimport.py:71`): the file cannot be opened, no text at all
  (`trelby/pdfimport.py:959`), a bad profile; with `strict`, also every
  case listed under "Lenient reading" below.

## Stages

1. **Extract** (`extractPages`, `trelby/pdfimport.py:281`): pdfplumber
   words per page, sorted by top then x; words whose top is within 2 pt of
   the line's first word form one line (`trelby/pdfimport.py:298`).
   `lineNo` counts every text line of the page, furniture included.
2. **Detect the layout** (`detectLayout`, `trelby/pdfimport.py:341`), when
   no profile is given. Builds the same `Profile` a TOML file would, with a
   human-readable `summary`:
   1. title page: page 1 with no scene heading and at most 20 lines is
      skipped, as an issue (`trelby/pdfimport.py:347`);
   2. page numbers: a lone number (`NUMBER_RE`) as the first or last line
      of a page → a drop rule bounded by those lines' tops; the
      `STANDARD_DROPS` (`(MORE)`, `(MAIS)`, `CONTINUED`, `CONTINUAÇÃO`, …,
      `trelby/pdfimport.py:57`) always apply (`trelby/pdfimport.py:359`);
   3. margin scene numbers: a number more than 10 pt left or right of a
      scene heading (`trelby/pdfimport.py:378`);
   4. scene headings by `SCENE_RE` (`trelby/pdfimport.py:48`: optional typed
      number, then `INT`, `EXT`, `EST`, `I/E`, `INT./EXT.`, with or without
      the dot); their most common indent is the scene/action indent
      (`trelby/pdfimport.py:399`);
   5. character cues: short upper-case lines right of that indent, followed
      without a blank line by more text; most common left edge, or center
      if fewer than 60% share an edge (`trelby/pdfimport.py:416`). The line
      step is the **smallest** common vertical step, not the most common
      (`trelby/pdfimport.py:428`); the paragraph gap is 1.5 × that;
   6. dialogue / parenthetical indents: what follows a cue
      (`trelby/pdfimport.py:458`);
   7. transitions: upper-case lines ending in `:` or `FADE OUT` at no other
      indent, by left edge or right edge (`trelby/pdfimport.py:485`);
   8. dual dialogue: two short upper-case columns on one line, and the
      column indents of the lines under them (`trelby/pdfimport.py:502`).

   Typed scene numbers (`12. INT. …`) are always recognized; with three or
   more of them, an upper-case numbered line without INT./EXT. is also a
   heading (`trelby/pdfimport.py:561`), reported as an issue.
3. **Per line** (`_items`, `trelby/pdfimport.py:659`), skipped pages
   traced (`trelby/pdfimport.py:669`): drop rules
   (`trelby/pdfimport.py:683`); margin scene numbers removed
   (`trelby/pdfimport.py:691`); split into segments at gaps wider than
   `segment_gap` (`_split`, `trelby/pdfimport.py:311`); two segments that
   classify as characters by the dual rules start a dual-dialogue block
   (`trelby/pdfimport.py:715`), inside which every segment is classified by
   the column rules; otherwise one segment classified by the indent rules
   (`_classify`, `trelby/pdfimport.py:630`), first match wins; a scene
   heading gets ` #n#` appended, the margin number winning over the typed
   one (`trelby/pdfimport.py:780`).
4. **Elements** (`_elements`, `trelby/pdfimport.py:802`): a new element
   starts on a type change, a column/block change, every character and
   transition line, a parenthetical line starting with `(`, a vertical gap
   above `paragraph_gap`, or a new page unless the line is dialogue
   (`startsNew`, `trelby/pdfimport.py:810-821`). Character names lose their
   suffixes (`(CONT'D)`, …); a cue at the top of a page repeating the speaker
   of the speech that ended the previous page is dropped, so the speech goes
   on (`trelby/pdfimport.py:831-838`). Each dual column continues from its
   own previous item (`trelby/pdfimport.py:808`); the right column's cue
   gets ` ^` (`trelby/pdfimport.py:864`) and its elements move after the
   left column's (`trelby/pdfimport.py:872`).
5. **Checks** (`_checkElements`, `trelby/pdfimport.py:895`): a character
   cue with no parenthetical or dialogue after it (usually a speech typed at
   the action indent) is an issue on that cue.
6. **Out** (`importPdf`): layout issues first, then each element preceded
   by its items' issues as `NOTE` lines (`_noteText`,
   `trelby/pdfimport.py:907`); issues also go to `issues` and, as `ISSUE`
   rows, to the trace.

## Lenient reading (each an issue and a note; a stop with `strict`)

- A line at no known indent → the nearest rule's element (`_nearest`,
  `trelby/pdfimport.py:654`), `unusual indent (x0 …) read as …`
  (`trelby/pdfimport.py:765-771`).
- Two or more columns that are not dual dialogue → read as one line
  (`trelby/pdfimport.py:723`).
- A dual-dialogue segment at no column indent → the nearest column rule
  (`trelby/pdfimport.py:751`); more than two columns inside a block → the
  extra columns join the right one.

## Other entry points

- `probe(path, skipPages, segmentGap)` (`trelby/pdfimport.py:973`): one row
  per (x0, column) with count, right-edge range and three sample lines,
  then the detected layout and its issues.
- `report(path, layout, issues)` (`trelby/pdfimport.py:1025`): the text of
  the GUI's import report.
- `writeTrace(trace, path)` (`trelby/pdfimport.py:1015`): TSV, columns
  `page line top x0 x1 decision rule text`. Decisions: an element name,
  `<element> (nearest)`, `dual left|right <element>`, `dropped`,
  `scene number`, `skipped page`, `UNKNOWN INDENT` (strict stop), `ISSUE`.
- `toScreenplay(lines)` (`trelby/pdfimport.py:1044`): a `Screenplay` with
  **no title pages** (`trelby/pdfimport.py:1054`), reformatted and
  paginated, for `generateFountain`.
- `main(argv)` (`trelby/pdfimport.py:1061`), `python -m trelby.pdfimport`:
  `import <pdf>... --out <dir> [--profile <toml>] [--skip-pages N]
  [--strict] [--no-notes] [--trace]` writes `<name>.fountain` (notes as
  `[[IMPORT: …]]`) and `<name>.trace.tsv`, prints the layout, each issue on
  stderr (`trelby/pdfimport.py:1129`) and the element counts; exit 1 if any
  PDF failed. `probe <pdf> [--skip-pages N] [--segment-gap G]`.

## Gotchas

- **Action cut by a page break becomes two paragraphs:** only dialogue
  continues across pages (`trelby/pdfimport.py:820-821`).
- Lines are rejoined with single spaces: multiple spaces collapse, a word
  cut over two lines gets a space inside it, and a hyphen at a line end
  stays (`bem- vindo`).
- A heading without INT./EXT. is found only when typed with a number in a
  script that numbers its headings; otherwise it comes back as action, with
  no issue.
- Detection needs some material: a PDF with no character cue gets an issue
  and every line right of the action indent is read by its nearest rule.
- Trelby has no dual-dialogue or scene-number fields: `^` and `#n#` stay in
  the element text in the editor; in the Fountain export they are valid
  Fountain markup.
- Fixed 2 pt tolerance for grouping words into a line
  (`trelby/pdfimport.py:298`), not a profile key.
- The title page is not imported; the CLI output has no Fountain title
  block.

## Tests

`tests/test_pdfimport.py` draws its PDFs with ReportLab at test time:
classification with the profile `tests/fixtures/pdf/letter-test.toml`,
detection checked against that profile's result, and Trelby's own PDF export
of `test.trelby` detected and through `trelby-a4.toml`.
