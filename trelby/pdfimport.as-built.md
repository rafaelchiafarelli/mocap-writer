# pdfimport.py — as built

`trelby/pdfimport.py` turns a master-scene screenplay PDF with selectable
text into a list of `Line`s, classifying each line by its horizontal
position. The layout is **detected from the PDF itself** (`detectLayout`);
a TOML layout profile (`pdfprofiles/CLAUDE.md`) can be given instead, from
the command line only. Deterministic, no LLM, no wx at import time;
`pdfplumber` is imported only when a PDF is read
(`trelby/pdfimport.py:283`). The GUI wrapper is `myimport.importPdf`
(`trelby/myimport.py:399`).

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
  (`trelby/pdfimport.py:931`).
- Out: `list[Line]` meeting the importer contract of `myimport.as-built.md`:
  every line `LB_SPACE`, the last line of each element `LB_LAST`, notes as
  one-line `NOTE` elements, so the caller's `reformatAll` re-wraps them.
- Errors (`PdfImportError`, `.page` / `.lineNo`,
  `trelby/pdfimport.py:72`): the file cannot be opened, no text at all
  (`trelby/pdfimport.py:974`), a bad profile; with `strict`, also every
  case listed under "Lenient reading" below.

## Stages

1. **Extract** (`extractPages`, `trelby/pdfimport.py:282`): pdfplumber
   words per page, sorted by top then x; words whose top is within 2 pt of
   the line's first word form one line (`trelby/pdfimport.py:299`).
   `lineNo` counts every text line of the page, furniture included.
2. **Detect the layout** (`detectLayout`, `trelby/pdfimport.py:342`), when
   no profile is given. Builds the same `Profile` a TOML file would, with a
   human-readable `summary`:
   1. title page: page 1 with no scene heading and at most 20 lines is
      skipped, as an issue (`trelby/pdfimport.py:348`);
   2. page numbers: a lone number (`NUMBER_RE`) as the first or last line
      of a page → a drop rule bounded by those lines' tops; the
      `STANDARD_DROPS` (`(MORE)`, `(MAIS)`, `CONTINUED`, `CONTINUAÇÃO`, …,
      `trelby/pdfimport.py:58`) always apply (`trelby/pdfimport.py:360`);
   3. margin scene numbers: a number more than 10 pt left or right of a
      scene heading (`trelby/pdfimport.py:379`);
   4. scene headings by `SCENE_RE` (`trelby/pdfimport.py:49`: optional typed
      number, then `INT`, `EXT`, `EST`, `I/E`, `INT./EXT.`, with or without
      the dot); their most common indent is the scene/action indent
      (`trelby/pdfimport.py:400`);
   5. character cues: short upper-case lines right of that indent, followed
      without a blank line by more text; most common left edge, or center
      if fewer than 60% share an edge (`trelby/pdfimport.py:417`). The line
      step is the **smallest** common vertical step, not the most common
      (`trelby/pdfimport.py:429`); the paragraph gap is 1.5 × that;
   6. dialogue / parenthetical indents: what follows a cue
      (`trelby/pdfimport.py:459`);
   7. transitions: upper-case lines ending in `:` or `FADE OUT` at no other
      indent, by left edge or right edge (`trelby/pdfimport.py:486`);
   8. dual dialogue: two short upper-case columns on one line, and the
      column indents of the lines under them (`trelby/pdfimport.py:503`).

   Typed scene numbers (`12. INT. …`) are always recognized; with three or
   more of them, an upper-case numbered line without INT./EXT. is also a
   heading (`trelby/pdfimport.py:562`), reported as an issue.
3. **Per line** (`_items`, `trelby/pdfimport.py:660`), skipped pages
   traced (`trelby/pdfimport.py:670`): drop rules
   (`trelby/pdfimport.py:684`); margin scene numbers removed
   (`trelby/pdfimport.py:692`); split into segments at gaps wider than
   `segment_gap` (`_split`, `trelby/pdfimport.py:312`); two segments that
   classify as characters by the dual rules start a dual-dialogue block
   (`trelby/pdfimport.py:716`), inside which every segment is classified by
   the column rules; otherwise one segment classified by the indent rules
   (`_classify`, `trelby/pdfimport.py:631`), first match wins; a scene
   heading gets ` #n#` appended, the margin number winning over the typed
   one, and `importPdf` moves it to the first line's `num`
   (`_splitSceneNumber`; fountain-native/scenes/2) (`trelby/pdfimport.py:781`).
4. **Elements** (`_elements`, `trelby/pdfimport.py:812`): a new element
   starts on a type change, a column/block change, every character and
   transition line, a parenthetical line starting with `(`, a vertical gap
   above `paragraph_gap`, or a new page unless the line is dialogue
   (`startsNew`, `trelby/pdfimport.py:820-831`). Character names lose their
   suffixes (`(CONT'D)`, …); a cue at the top of a page repeating the speaker
   of the speech that ended the previous page is dropped, so the speech goes
   on (`trelby/pdfimport.py:841-848`). Each dual column continues from its
   own previous item (`trelby/pdfimport.py:818`); the right column's cue
   gets ` ^` (`trelby/pdfimport.py:874`) and its elements move after the
   left column's (`trelby/pdfimport.py:882`).
5. **Checks** (`_checkElements`, `trelby/pdfimport.py:905`): a character
   cue with no parenthetical or dialogue after it (usually a speech typed at
   the action indent) is an issue on that cue.
6. **Out** (`importPdf`): layout issues first, then each element preceded
   by its items' issues as `NOTE` lines (`_noteText`,
   `trelby/pdfimport.py:917`); issues also go to `issues` and, as `ISSUE`
   rows, to the trace.

## Lenient reading (each an issue and a note; a stop with `strict`)

- A line at no known indent → the nearest rule's element (`_nearest`,
  `trelby/pdfimport.py:655`), `unusual indent (x0 …) read as …`
  (`trelby/pdfimport.py:766-772`).
- Two or more columns that are not dual dialogue → read as one line
  (`trelby/pdfimport.py:724`).
- A dual-dialogue segment at no column indent → the nearest column rule
  (`trelby/pdfimport.py:752`); more than two columns inside a block → the
  extra columns join the right one.

## Other entry points

- `probe(path, skipPages, segmentGap)` (`trelby/pdfimport.py:988`): one row
  per (x0, column) with count, right-edge range and three sample lines,
  then the detected layout and its issues.
- `report(path, layout, issues)` (`trelby/pdfimport.py:1040`): the text of
  the GUI's import report.
- `writeTrace(trace, path)` (`trelby/pdfimport.py:1030`): TSV, columns
  `page line top x0 x1 decision rule text`. Decisions: an element name,
  `<element> (nearest)`, `dual left|right <element>`, `dropped`,
  `scene number`, `skipped page`, `UNKNOWN INDENT` (strict stop), `ISSUE`.
- `toScreenplay(lines)` (`trelby/pdfimport.py:1059`): a `Screenplay` with
  **no title pages** (`trelby/pdfimport.py:1069`), reformatted and
  paginated, for `fountain.generate`.
- `main(argv)` (`trelby/pdfimport.py:1076`), `python -m trelby.pdfimport`:
  `import <pdf>... --out <dir> [--profile <toml>] [--skip-pages N]
  [--strict] [--no-notes] [--trace]` writes `<name>.fountain` (notes as
  `[[IMPORT: …]]`) with `fountain.generate` and `<name>.trace.tsv`, prints
  the layout, each issue on stderr (`trelby/pdfimport.py:1144`), each element
  the writer could not keep as `lost: <file>: <text>` on stderr
  (`trelby/pdfimport.py:1151-1158`) and the element counts; exit 1 if any
  PDF failed. `probe <pdf> [--skip-pages N] [--segment-gap G]`.

## Gotchas

- **Action cut by a page break becomes two paragraphs:** only dialogue
  continues across pages (`trelby/pdfimport.py:830-831`).
- Lines are rejoined with single spaces: multiple spaces collapse, a word
  cut over two lines gets a space inside it, and a hyphen at a line end
  stays (`bem- vindo`).
- A heading without INT./EXT. is found only when typed with a number in a
  script that numbers its headings; otherwise it comes back as action, with
  no issue.
- Detection needs some material: a PDF with no character cue gets an issue
  and every line right of the action indent is read by its nearest rule.
- Trelby has no dual-dialogue field: `^` stays in the element text in the
  editor; in the Fountain export it is valid Fountain markup. A scene
  number is the heading line's `num` (written as `#n#`); a number not in
  the writer's form (`7A`) is kept and reported when the script is opened.
- Fixed 2 pt tolerance for grouping words into a line
  (`trelby/pdfimport.py:299`), not a profile key.
- The title page is not imported; the CLI output has no Fountain title
  block.

## Tests

`tests/test_pdfimport.py` draws its PDFs with ReportLab at test time:
classification with the profile `tests/fixtures/pdf/letter-test.toml`,
detection checked against that profile's result, and Trelby's own PDF export
of `test.fountain` detected and through `trelby-a4.toml`.
