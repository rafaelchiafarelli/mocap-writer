# screenplay.py — as built

`trelby/screenplay.py` (3213 lines) holds the script model and almost all
behaviour that does not need wx: editing commands, wrapping, pagination,
undo bookkeeping and every export (the `.trelby` load/save was removed
2026-10-25; files are Fountain, `trelby/fountain.py`). It imports `wx`
(`trelby/screenplay.py:2`) but does not use it in the code paths the tests
run.

## Constants

- Line breaks (`trelby/screenplay.py:6-14`): `LB_SPACE` 1, `LB_SPACE2` 2
  (read-only, old files), `LB_NONE` 3, `LB_FORCED` 4, `LB_LAST` 5.
- Line types (`trelby/screenplay.py:17-25`): `SCENE` 1, `ACTION` 2,
  `CHARACTER` 3, `DIALOGUE` 4, `PAREN` 5, `TRANSITION` 6, `SHOT` 7, `NOTE` 8,
  `ACTBREAK` 9. The values are written nowhere: files use the one-character
  codes from `config._init` (`trelby/config.py:1791-1810`).
- The constants are defined **before** the imports
  (`trelby/screenplay.py:4-47`) because `config` and `line` import
  `screenplay` back (circular import).

## Classes

- `Screenplay` (`trelby/screenplay.py:51`). State (`trelby/screenplay.py:52-129`):
  - `lines: list[Line]` — never empty; a new script is one empty Scene line;
  - `sceneNumbersIssued` — the scene numbers it had when opened or last
    saved (`fountain.load`, `scenenumbers.prepareSave`); one gone is
    written back as `OMITTED` (fountain-native/scenes/3);
  - `sceneTextsIssued` — `{number: text}` of those scenes, to tell a moved
    scene at the next save; `sceneMoves` — `{old: new}` renames since the
    last save, emptied by the save that rewrites the film's records
    (fountain-native/scenes/5);
  - `fountainSource` — the `fountain.Source` of the `.fountain` it was
    opened from or last saved to, else `None` (`trelby/screenplay.py:70`);
    `__deepcopy__` shares it (`trelby/screenplay.py:182`);
  - `line`, `column` — cursor; `_topLine` — first line on screen
    (`getTopLine` / `setTopLine` clamp it, `trelby/screenplay.py:823-830`);
  - `mark: Mark | None` — the other end of the selection;
  - `pages`, `pagesNoAdjust` — page table (see Pagination);
  - `acItems`, `acSel`, `acMax` — open auto-completion list;
  - `hasChanged`; `firstUndo` / `lastUndo` / `currentUndo` /
    `undoMemoryUsed` — undo chain;
  - `cfg: config.Config` (per script), `cfgGl` (shared global config),
    `titles`, `headers`, `locations`, `autoCompletion`, `scDict`.
- `Mark(line, column)` (`trelby/screenplay.py:3174`), `ClipData`
  (`lines`, `trelby/screenplay.py:3184`), `CommandState`
  (`doAutoComp` = `AC_DEL` / `AC_REDO` / `AC_KEEP`, `char`, `mark`,
  `needsVisifying`, `trelby/screenplay.py:3192`).

## Data-structure invariants

Checked by `_validate` (`trelby/screenplay.py:3135`, test code only):
- at least one line; cursor inside the script and inside its line;
- every line's text equals `util.toInputStr(text)`;
- `len(text.rstrip(" "))` ≤ the type's `width` — trailing spaces may run
  past the width (`trelby/screenplay.py:889-916`);
- an `LB_NONE` line does not end in a space;
- all lines of one element have the same type (an element ends at
  `LB_LAST`).

`_validate` checks them (`trelby/screenplay.py:3135`). Paragraph = lines up to `LB_FORCED` /
`LB_LAST`; element = lines up to `LB_LAST`; scene = from a `SCENE` or
`ACTBREAK` element to the next (`getSceneIndexesFromLine`,
`trelby/screenplay.py:1148`).

## Key functions

Settings
- `applyCfg(cfg)` replaces the script config, **clears undo**, re-wraps and
  re-paginates (`trelby/screenplay.py:197`).
- `__deepcopy__` is hand-written for speed and copies lines, config, titles,
  headers, locations, completion and dictionary, and the cursor — not undo
  history (`trelby/screenplay.py:173`); lines with `Line.copy`, so scene
  numbers are kept.

Layout
- `wrapLine` (`trelby/screenplay.py:868`), `rewrapPara`
  (`trelby/screenplay.py:934`), `rewrapPrevPara`, `rewrapElem`
  (`trelby/screenplay.py:1001`), `reformatRange`
  (`trelby/screenplay.py:848`), `reformatAll` (`trelby/screenplay.py:835`).
  The scene number (`Line.num`) stays on the first line of what is
  wrapped (`trelby/screenplay.py:927`, `trelby/screenplay.py:965`).
  Parentheticals wrap one character narrower after their first line and are
  drawn one character further right (`needsExtraParenIndent`,
  `trelby/screenplay.py:149`).
- `getSpacingBefore(i)` — `beforeSpacing` at an element start, else
  `intraSpacing`, in tenths of a line (`trelby/screenplay.py:152`).

Pagination
- `paginate()` (`trelby/screenplay.py:1230`): `pages = [-1, last line of
  page 1, …]`. Page capacity `linesOnPage * 10` minus headers, minus 20 for
  `CONTINUED:` and 10 for `(cont'd)` on later pages, never below 50.
  Break adjustment by type of the last line (`trelby/screenplay.py:1296-1374`,
  `removeDanglingElement` `trelby/screenplay.py:1385`).
  `lastPaginated` is set for the editor's timed re-pagination.
- `line2page`, `line2pageNoAdjust` (binary search,
  `trelby/screenplay.py:1571-1589`), `page2lines` (`trelby/screenplay.py:1610`),
  `getPageNumbers` (`trelby/screenplay.py:1620`), `needsMore`
  (`trelby/screenplay.py:1195`), `getPrevSpeaker` (`trelby/screenplay.py:1207`).

Editing commands (`cmd(name)` calls `<name>Cmd` then `cmdPost`,
`trelby/screenplay.py:2489`)
- Movement: `moveLeftCmd` … `moveSceneDownCmd`
  (`trelby/screenplay.py:2505-2674`). Up/Down move the completion selection
  when a list is open (`trelby/screenplay.py:2525-2550`).
- Text: `addCharCmd` (`trelby/screenplay.py:2889`), `deleteBackwardCmd`
  (`trelby/screenplay.py:2676`), `deleteForwardCmd`
  (`trelby/screenplay.py:2731`), `insertForcedLineBreakCmd`
  (`trelby/screenplay.py:2845`).
- Elements: `splitElementCmd` (Enter, `trelby/screenplay.py:2856`),
  `tabCmd` (`trelby/screenplay.py:2865`), `toPrevTypeTabCmd`
  (`trelby/screenplay.py:2879`), `to<Type>Cmd` (`trelby/screenplay.py:2994-3019`)
  → `convertTypeTo(lt, saveUndo)` (`trelby/screenplay.py:1412`, works on the
  selection's elements if any; empty parenthetical ↔ `()`).
- Selection and clipboard: `getMarkedLines`, `getMarkedColumns`,
  `getSelectedAsCD(doDelete)` (cut/copy, `trelby/screenplay.py:1878`),
  `paste(clines)` (`trelby/screenplay.py:1989`), `selectSceneCmd`,
  `selectAllCmd`, `selectWordAt(line, col)` (the word under a double
  click, or one ending just before `col`; False on a space or punctuation,
  `trelby/screenplay.py:2802`), `selectElementAt(line)` (a triple click,
  `trelby/screenplay.py:2830`). Neither cut nor copy puts a scene number on the
  clipboard, so a pasted scene has none; pasting several elements at the
  start of a heading leaves its number with the heading's text
  (`trelby/screenplay.py:2036`, `trelby/screenplay.py:2050-2052`). `joinLines` drops the number of the
  line joined in, unless the line it joins is empty and has none
  (`trelby/screenplay.py:1489-1490`).
- Other: `removeElementTypes(tdict, saveUndo)` (`trelby/screenplay.py:2420`),
  `findError(line)` (`trelby/screenplay.py:2155`), `getWord` (spell checker,
  `trelby/screenplay.py:1664`), `capitalizeNeeded`
  (`trelby/screenplay.py:2086`).
- Queries for reports and dialogs: `getSceneLocations` (the numbered
  scenes, `[(number, line)]`, for Go to scene, `trelby/screenplay.py:1630`),
  `getSceneNames` (`trelby/screenplay.py:1637`), `getCharacterNames`
  (`trelby/screenplay.py:1648`), `getCharCount`
  (`trelby/screenplay.py:1227`).

Undo (`trelby/screenplay.py:3022-3131`)
- Doubly linked list of `undo.*` objects. A new edit while inside the
  history cuts off the redo part (`trelby/screenplay.py:3041-3065`).
  History is trimmed from the oldest end once the estimate reaches
  5 000 000 bytes (`trelby/screenplay.py:3080-3093`).
- Merging: consecutive `addChar` (word-level, spaces join the preceding
  word), `deleteBackward`, `deleteForward` merge when the cursor is where
  the last step left it (`trelby/screenplay.py:2684-2689`,
  `trelby/screenplay.py:2919-2942`).

Export
- `generateText(doPages)` (`trelby/screenplay.py:216`), `generateHtml(includeNotes)`
  (`trelby/screenplay.py:250`), `getElementsAsList()` → `[(lt, text)]` with
  forced breaks as `\n` and export caps applied (`trelby/screenplay.py:342`),
  `generateFDX` (`trelby/screenplay.py:367`), `generateRTF`
  (`trelby/screenplay.py:416`); Fountain is written by `fountain.generate`,
  not here (`fountain.as-built.md`),
  `generatePDF(isExport)` / `generatePML(isExport)`
  (`trelby/screenplay.py:520-554`; after the title pages, `frontPages(doc)`
  when set adds a film's front matter pages, not counted as the script's,
  front-matter/print/1), `generatePMLPage(pager, pageNr, forPDF,
  doExtra)` (`trelby/screenplay.py:566`; `forPDF=False` is the screen
  layout, `doExtra=False` skips headers and styling and is used only for
  position queries; with `forPDF=True` Act break lines are not drawn and
  take no space, `trelby/screenplay.py:656-672`, so a PDF page ends a
  little short where it held one). Scene numbers are the labels of
  `scenenumbers.labels` (permanent, or `(12.A)` for one a save would
  give), drawn when `pdfShowSceneNumbers` is on or always on screen
  (`trelby/screenplay.py:598`), also in the TOC and next to a page-top
  `CONTINUED:`; `addSceneNumbers` (`trelby/screenplay.py:811`) puts the
  label left of the heading, right-aligned to it, and right of it, and
  tags both ops with `sceneLine` (the heading's line) for the click on
  screen, `compareScripts(sp2) -> bytes | None`
  (`trelby/screenplay.py:2248`).

## Extension points

- **Element types.** A new type needs: a constant here
  (`trelby/screenplay.py:17-25`); a code character and name in
  `config._init` (`trelby/config.py:1791`); per-script defaults in
  `Config.__init__` (`trelby/config.py:447-514`); an Enter/Tab row in
  `ConfigGlobal.__init__` (`trelby/config.py:695-739`); a `ChangeTo<Type>`
  command in the alphabetical command list (`trelby/config.py:742`), a
  `cmdChangeTo<Type>` in `MyCtrl` (`trelby/trelbyctrl.py:1612-1638`) and a
  `to<Type>Cmd` here (`trelby/screenplay.py:2994-3019`); a menu id in
  `trelby/ids.py:83-103` and the right-click menu
  (`trelby/trelbyframe.py:349-357`); entries in the export maps `htmlMap`
  (`trelby/screenplay.py:254`), `xmlMap` (`trelby/screenplay.py:375`) and
  `trelby/fountain.py` (parse and generate); pagination rules if it should not end a page
  (`trelby/screenplay.py:1298-1374`); `findError` rules if it has sequencing
  constraints.
- **Enter/Tab behaviour** is data, not code: `splitElementCmd` / `tabCmd`
  read `cfgGl.getType(lt).newTypeEnter|newTypeTab` and
  `cfgGl.nextTypeTab(lt)` / `prevTypeTab(lt)`, the `tabOrder` cycle
  (`trelby/screenplay.py:2857`, `trelby/screenplay.py:2871-2876`,
  `trelby/screenplay.py:2885-2886`); the table is in
  `trelby/config.py:695-739`. `tabMakesNew` decides "new element vs.
  convert" (`trelby/screenplay.py:1713`).
- **Typing rules** (auto-capitalize, `INT.`/`EXT.` → Scene, `(` → Paren) are
  hard-coded in `addCharCmd` (`trelby/screenplay.py:2944-2981`) and
  `capitalizeNeeded` (`trelby/screenplay.py:2086`); only the two capitalize
  switches are settings.
- **Import** produces `lines` only; whatever imports must give lines that
  satisfy the invariants above before `reformatAll` + `paginate`
  (`trelby/trelbyctrl.py:474-476`).

## Gotchas

- `reformatAll` asserts there is no undo history
  (`trelby/screenplay.py:832`); `applyCfg` clears undo for that reason
  (`trelby/screenplay.py:199-202`).
- Element-type sequencing (Character → Dialogue, etc.) is **not enforced**
  while editing; only `findError` reports it, before export/print when
  `checkOnExport` is on.
- `Config.cursorLine` / `cursorColumn` and `cfgGl.honorSavedPos` are left
  from the `.trelby` format: nothing writes or reads the saved cursor now.
- Accepting a completion with End (`moveLineEndCmd`,
  `trelby/screenplay.py:2620-2635`) replaces only the current screen line's
  text, as Enter does, then re-wraps; it is one `SinglePara` undo step.
- `generateHtml` uses one `<pre>` per screen line, not per element
  (`trelby/screenplay.py:326-334`).
- `generateFDX` writes notes as an Action paragraph wrapping a `ScriptNote`,
  all with `ID="1"` (`trelby/screenplay.py:389-394`).

## Tests

- Editing: `tests/test_addchar.py`, `tests/test_changetype.py`,
  `tests/test_copypaste.py`, `tests/test_cut.py`, `tests/test_delete.py`,
  `tests/test_join_elems.py`, `tests/test_movement.py`,
  `tests/test_ismodified.py`.
- Invariants: `tests/test_validate.py` (via `tests/u.py`, fixture
  `tests/fixtures/test.fountain` + `test.sconf`).
- PDF: `tests/test_renderscreenplay.py` (default and custom TTF font).
- Indirectly: the report tests and `tests/test_myimport.py`.
- **Not covered**: `generateFDX`,
  `generateHtml`, `generateRTF`, `generateText`, `compareScripts`,
  `paginate` results, undo/redo. `tests/execute_random_tests.py` is a
  manual random-operation fuzzer, not part of the suite.
