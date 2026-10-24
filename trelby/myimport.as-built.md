# myimport.py — as built

`trelby/myimport.py` (940 lines) turns foreign script files into a list of
`Line` objects. It has one function per format and no shared importer
interface. The caller, `MyCtrl.importFile` (`trelby/trelbyctrl.py:167`),
picks the function by the file name's ending and replaces the tab's script
with the result.

## Contract (shared by every importer)

- In: `fileName` (str), `frame` (wx parent for message boxes and option
  dialogs); `importFountain` also takes `titlePages`.
- Out: `list[Line]`, or `None` after showing the user an error. The list
  must satisfy the `Screenplay` invariants: every element's lines share one
  type, the last line is `LB_LAST`
  (`screenplay.as-built.md`, Data-structure invariants). Lines need not be
  wrapped: the caller runs `reformatAll()` and `paginate()`
  (`trelby/trelbyctrl.py:189-193`).
- Most importers emit each source line as `LB_FORCED` and the element's
  last line as `LB_LAST` (e.g. `trelby/myimport.py:63-72`), so line breaks
  inside an element survive as forced breaks.
- Text goes through `util.cleanInput` / `util.toInputStr`, which only drop
  form feeds and turn tabs into `|` (`trelby/util.py:233-245`); characters
  outside Latin-1 are kept.
- Unknown element names become Action.

## Functions

- `importAstx` (`trelby/myimport.py:29`) — Adobe Story XML:
  `/AdobeStory/document/stream/section/scene/paragraph`, attribute
  `element` → type, `textRun` / `break` children → lines.
- `importFadein` (`trelby/myimport.py:99`) — `.fadein` zip →
  `document.xml` (Open Screenplay Format): `paragraphs/para`, `style
  @basestylename` → type, `<br>` → line break, inline formatting tags
  removed (`sanitizeStr`, `trelby/myimport.py:163`); `note` / `synopsis`
  attributes → Note elements; a Parenthetical gets `(`…`)` added if missing.
- `importCeltx` (`trelby/myimport.py:219`) — `.celtx` zip → first member
  whose name starts with `script` (HTML): `/html/body/p`, `class` → type
  (`act` → Act break).
- `importFDX` (`trelby/myimport.py:300`) — Final Draft XML:
  `Content//Paragraph`, `Type` → type; `ScriptNote/Paragraph/Text` → a Note
  element before the paragraph; `General` paragraphs (dual-dialogue
  wrappers) skipped, their inner paragraphs imported; U+2028 → newline.
- `importFountain(fileName, frame, titlePages)` (`trelby/myimport.py:395`)
  — returns `(lines, titlePages)`:
  1. options dialog: title page, titles as action, strip markup,
     sections/synopses as notes (`trelby/myimport.py:449-466`);
  2. newlines normalized, boneyard `/* … */` removed
     (`trelby/myimport.py:469-471`);
  3. title block = lines before the first blank line, if the first one has
     exactly one `:` and does not start with `fade`
     (`trelby/myimport.py:484-499`); `Title`, `Author(s)` (prefixed `by`),
     `Contact` overwrite the default title strings 0–2, `Credit` / `Source`
     are added centered, other keys added on the left
     (`trelby/myimport.py:501-568`);
  4. first pass, one `Line` per source line, classified in this order
     (`trelby/myimport.py:645-728`): blank / centered `>…<` / page break
     `===` → Action; two spaces → previous type; scene (`.` forced, or
     `INT`/`EXT`/`EST`/`INT./EXT`/`I/E` + space or dot, not ending in two
     spaces, `trelby/myimport.py:610-622`); transition (upper-case ending
     `TO:`, or `>` without closing `<`, between blank lines); character
     (all caps after a blank line, followed by a non-blank line, not ending
     in two spaces); parenthetical after character/dialogue; dialogue after
     character/dialogue/paren; `[[note]]`; `#` section / `=` synopsis →
     Note or dropped. Centered action is indented to the middle of the
     Action width (`trelby/myimport.py:714-721`); `^` (dual dialogue) is
     stripped from character names when markup is removed;
  5. second pass merges consecutive same-type lines into elements and turns
     blank lines into element ends (`trelby/myimport.py:744-758`).
- `importTextFile(fileName, frame)` (`trelby/myimport.py:765`) — indented
  plain text (the format of Trelby's own text export):
  1. per indentation width, an `Indent` counts lines, `INT.`/`EXT.`
     starts, `CUT TO:`/`DISSOLVE TO:` and `(…)` lines
     (`trelby/myimport.py:785-813`);
  2. `setType` assigns types greedily: most scene starts → Scene/Action
     mix, most lines → Dialogue, next → Character, most transitions →
     Transition, most parens → Parenthetical, then the indent one deeper
     than Parenthetical also Parenthetical; the rest Action
     (`trelby/myimport.py:820-854`, `setType` `trelby/myimport.py:914`);
  3. `ImportDlg` lets the user change the type of each indent or ignore it
     (`trelby/myimport.py:856`);
  4. lines become `LB_SPACE` lines (so they re-wrap), a blank line ends an
     element, `(CONT'D)` is cut from characters and `(continuing)`
     parentheticals dropped (`trelby/myimport.py:867-907`).
- Module constants `SCENE_ACTION` = −2 and `IGNORE` = −3 are extra
  pseudo-types used only by the text importer and `ImportDlg`
  (`trelby/myimport.py:21-25`).

## Extension points

- **A new format** (e.g. PDF): a new `import<Format>(fileName, frame) ->
  list[Line] | None` here that meets the contract above, an `elif` on the
  file-name ending in `MyCtrl.importFile` (`trelby/trelbyctrl.py:169-182`),
  and an entry in the import dialog's wildcard
  (`trelby/trelbyframe.py:614-639`). Text extracted from a PDF that keeps
  indentation could go through the `importTextFile` path (indent
  statistics + `ImportDlg`), which already handles Trelby's own text export
  layout.
- **Fountain import** is self-contained in `importFountain`; its helper
  predicates (`isScene`, `isTransition`, `isNote`, …,
  `trelby/myimport.py:589-642`) are nested functions, not reusable from
  outside.
- **Title page import** writes into `titlePages` (a `Titles.pages` list)
  in place; only Fountain does this today.

## Gotchas

- **`importFountain` returns a bare `None`** on a read error or empty file
  (`trelby/myimport.py:442-447`), but the caller unpacks two values
  (`trelby/trelbyctrl.py:176-178`) → `TypeError`. A cancelled options
  dialog returns `(None, titlePages)` correctly (`trelby/myimport.py:459-461`). Bug: [bugs/import-export/1](../initiatives/bugs/epics/import-export/tasks/1-fountain-import-none.md).
- `importFountain` reads `frame.panel.ctrl.sp.cfg` for the Action width
  (`trelby/myimport.py:718`), so it needs the real frame, not just any wx
  parent.
- `importFountain` indexes `prelines[titleIdx]` without a bounds check while
  gathering title keys (`trelby/myimport.py:518-531`); a file that is only a
  title block, with no blank line and no final newline after it, raises
  `IndexError`. Bug: [bugs/import-export/2](../initiatives/bugs/epics/import-export/tasks/2-fountain-import-title-only.md).
- The `kwPattern` range `[A-za-z]` also matches `[ \ ] ^ _` and the
  backtick (`trelby/myimport.py:503`), as in the exporter. Bug: [bugs/import-export/5](../initiatives/bugs/epics/import-export/tasks/5-title-keyword-pattern.md).
- Dead code: the `try: util.toLatin1(...) except: … .decode(...)` loop
  (`trelby/myimport.py:472-476`) can never take the `except` branch,
  because `toLatin1` encodes with `"ignore"` (`trelby/util.py:188-189`); its
  `.decode` on a `str` would fail if it did.
- Fountain features not handled: dual dialogue (only `^` removal),
  emphasis (removed, not kept as style), lyrics `~`, forced action `!`,
  forced character `@`, scene numbers `#1#`, page breaks (kept as Action
  text `===`).
- Celtx, Fade In, FDX, Astx: formatting (bold, italic) is dropped; FDX
  title pages are not imported.
- `importTextFile` uses `screenplay.Line` (`trelby/myimport.py:897`), which
  only works because `screenplay.py` re-exports `Line` from `line.py`.

## Tests

- `tests/test_myimport.py`: `importCeltx` against `tests/fixtures/test.celtx`
  and `importTextFile` against `tests/fixtures/test.txt`, each compared with
  `tests/fixtures/test.trelby` after reformatting; `wx` is replaced by a
  `Mock` whose dialogs return OK.
- Not covered: `importFountain`, `importFDX`, `importAstx`, `importFadein`,
  title-page import.
