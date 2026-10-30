# myimport.py — as built

`trelby/myimport.py` (609 lines) turns foreign script files into a list of
`Line` objects. It has one function per format and no shared importer
interface. The caller, `MyCtrl.importFile` (`trelby/trelbyctrl.py:394`),
picks the function by the file name's ending and replaces the tab's script
with the result. A `.fountain` is not imported here: `importFile` reads it
like Open, through `fountain.load` (fountain-native/io/5).

## Contract (shared by every importer)

- In: `fileName` (str), `frame` (wx parent for message boxes and option
  dialogs).
- Out: `list[Line]`, or `None` after showing the user an error. The list
  must satisfy the `Screenplay` invariants: every element's lines share one
  type, the last line is `LB_LAST`
  (`screenplay.as-built.md`, Data-structure invariants). Lines need not be
  wrapped: the caller runs `reformatAll()` and `paginate()`
  (`trelby/trelbyctrl.py:429-431`).
- Most importers emit each source line as `LB_FORCED` and the element's
  last line as `LB_LAST` (e.g. `trelby/myimport.py:62-71`), so line breaks
  inside an element survive as forced breaks.
- Text goes through `util.cleanInput` / `util.toInputStr`, which only drop
  form feeds and turn tabs into `|` (`trelby/util.py:233-245`); characters
  outside Latin-1 are kept.
- Unknown element names become Action.

## Functions

- `importAstx` (`trelby/myimport.py:28`) — Adobe Story XML:
  `/AdobeStory/document/stream/section/scene/paragraph`, attribute
  `element` → type, `textRun` / `break` children → lines.
- `importFadein` (`trelby/myimport.py:98`) — `.fadein` zip →
  `document.xml` (Open Screenplay Format): `paragraphs/para`, `style
  @basestylename` → type, `<br>` → line break, inline formatting tags
  removed (`sanitizeStr`, `trelby/myimport.py:162`); `note` / `synopsis`
  attributes → Note elements; a Parenthetical gets `(`…`)` added if missing.
- `importCeltx` (`trelby/myimport.py:218`) — `.celtx` zip → first member
  whose name starts with `script` (HTML): `/html/body/p`, `class` → type
  (`act` → Act break).
- `importFDX` (`trelby/myimport.py:299`) — Final Draft XML:
  `Content//Paragraph`, `Type` → type; `ScriptNote/Paragraph/Text` → a Note
  element before the paragraph; `General` paragraphs (dual-dialogue
  wrappers) skipped, their inner paragraphs imported; U+2028 → newline.
- `importTextFile(fileName, frame)` (`trelby/myimport.py:434`) — indented
  plain text (the format of Trelby's own text export):
  1. per indentation width, an `Indent` counts lines, `INT.`/`EXT.`
     starts, `CUT TO:`/`DISSOLVE TO:` and `(…)` lines
     (`trelby/myimport.py:454-482`);
  2. `setType` assigns types greedily: most scene starts → Scene/Action
     mix, most lines → Dialogue, next → Character, most transitions →
     Transition, most parens → Parenthetical, then the indent one deeper
     than Parenthetical also Parenthetical; the rest Action
     (`trelby/myimport.py:489-523`, `setType` `trelby/myimport.py:583`);
  3. `ImportDlg` lets the user change the type of each indent or ignore it
     (`trelby/myimport.py:525`);
  4. lines become `LB_SPACE` lines (so they re-wrap), a blank line ends an
     element, `(CONT'D)` is cut from characters and `(continuing)`
     parentheticals dropped (`trelby/myimport.py:536-576`).
- `importPdf(fileName, frame)` (`trelby/myimport.py:399`) — screenplay
  PDF, the GUI side of `trelby/pdfimport.py` (`pdfimport.as-built.md`):
  1. asks nothing: `pdfimport.importPdf` with the layout detected from the
     PDF, issues as `IMPORT:` notes in the script; an `OSError` or
     `PdfImportError` (unreadable file, no text) is shown in a message box
     → `None` (`trelby/myimport.py:413`);
  2. the import report (`pdfimport.report`: layout found, every issue) in a
     `misc.TextDlg` (`trelby/myimport.py:424`);
  3. **instrumented:** if `$MOCAP_WRITER_PDF_TRACE` names a directory,
     the trace is written there as `<name>.trace.tsv` and its path added to
     the report (`trelby/myimport.py:404-420`).
- Module constants `SCENE_ACTION` = −2 and `IGNORE` = −3 are extra
  pseudo-types used only by the text importer and `ImportDlg`
  (`trelby/myimport.py:20-24`).

## Extension points

- **A new format**: a new `import<Format>(fileName, frame) ->
  list[Line] | None` here that meets the contract above, an `elif` on the
  file-name ending in `MyCtrl.importFile` (`trelby/trelbyctrl.py:409-422`, by the lower-cased extension),
  and an entry in the import dialog's wildcard
  (`trelby/trelbyframe.py:993-1021`). PDF followed this path, with the
  wx-free work in its own module (`pdfimport.py`).

## Gotchas

- Celtx, Fade In, FDX, Astx: formatting (bold, italic) is dropped; FDX
  title pages are not imported.
- `importTextFile` uses `screenplay.Line` (`trelby/myimport.py:566`), which
  only works because `screenplay.py` re-exports `Line` from `line.py`.

## Tests

- `tests/test_myimport.py`: `importCeltx` against `tests/fixtures/test.celtx`
  and `importTextFile` against `tests/fixtures/test.txt`, each compared with
  `tests/fixtures/test.fountain` (with the old ending put back,
  `tests/u.py:69`) after reformatting; the real `wx`, with `ImportDlg`
  patched to answer OK.
- `tests/test_pdfimport.py`: `importPdf` with `wx` and `misc.TextDlg`
  patched on the module (no question asked, report shown, error box, trace
  file).
- Not covered: `importFDX`, `importAstx`, `importFadein`.
