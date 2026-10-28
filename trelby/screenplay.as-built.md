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
  codes from `config._init` (`trelby/config.py:1766-1785`).
- The constants are defined **before** the imports
  (`trelby/screenplay.py:4-47`) because `config` and `line` import
  `screenplay` back (circular import).

## Classes

- `Screenplay` (`trelby/screenplay.py:51`). State (`trelby/screenplay.py:52-111`):
  - `lines: list[Line]` — never empty; a new script is one empty Scene line;
  - `fountainSource` — the `fountain.Source` of the `.fountain` it was
    opened from or last saved to, else `None` (`trelby/screenplay.py:66`);
    `__deepcopy__` shares it (`trelby/screenplay.py:164`);
  - `line`, `column` — cursor; `_topLine` — first line on screen
    (`getTopLine` / `setTopLine` clamp it, `trelby/screenplay.py:796-803`);
  - `mark: Mark | None` — the other end of the selection;
  - `pages`, `pagesNoAdjust` — page table (see Pagination);
  - `acItems`, `acSel`, `acMax` — open auto-completion list;
  - `hasChanged`; `firstUndo` / `lastUndo` / `currentUndo` /
    `undoMemoryUsed` — undo chain;
  - `cfg: config.Config` (per script), `cfgGl` (shared global config),
    `titles`, `headers`, `locations`, `autoCompletion`, `scDict`.
- `Mark(line, column)` (`trelby/screenplay.py:3131`), `ClipData`
  (`lines`, `trelby/screenplay.py:3141`), `CommandState`
  (`doAutoComp` = `AC_DEL` / `AC_REDO` / `AC_KEEP`, `char`, `mark`,
  `needsVisifying`, `trelby/screenplay.py:3149`).

## Data-structure invariants

Checked by `_validate` (`trelby/screenplay.py:3092`, test code only):
- at least one line; cursor inside the script and inside its line;
- every line's text equals `util.toInputStr(text)`;
- `len(text.rstrip(" "))` ≤ the type's `width` — trailing spaces may run
  past the width (`trelby/screenplay.py:862-889`);
- an `LB_NONE` line does not end in a space;
- all lines of one element have the same type (an element ends at
  `LB_LAST`).

`_validate` checks them (`trelby/screenplay.py:3092`). Paragraph = lines up to `LB_FORCED` /
`LB_LAST`; element = lines up to `LB_LAST`; scene = from a `SCENE` or
`ACTBREAK` element to the next (`getSceneIndexesFromLine`,
`trelby/screenplay.py:1121`).

## Key functions

Settings
- `applyCfg(cfg)` replaces the script config, **clears undo**, re-wraps and
  re-paginates (`trelby/screenplay.py:176`).
- `__deepcopy__` is hand-written for speed and copies lines, config, titles,
  headers, locations, completion and dictionary, and the cursor — not undo
  history (`trelby/screenplay.py:155`); lines with `Line.copy`, so scene
  numbers are kept.

Layout
- `wrapLine` (`trelby/screenplay.py:841`), `rewrapPara`
  (`trelby/screenplay.py:907`), `rewrapPrevPara`, `rewrapElem`
  (`trelby/screenplay.py:974`), `reformatRange`
  (`trelby/screenplay.py:821`), `reformatAll` (`trelby/screenplay.py:805`).
  The scene number (`Line.num`) stays on the first line of what is
  wrapped (`trelby/screenplay.py:900`, `trelby/screenplay.py:938`).
  Parentheticals wrap one character narrower after their first line and are
  drawn one character further right (`needsExtraParenIndent`,
  `trelby/screenplay.py:131`).
- `getSpacingBefore(i)` — `beforeSpacing` at an element start, else
  `intraSpacing`, in tenths of a line (`trelby/screenplay.py:134`).

Pagination
- `paginate()` (`trelby/screenplay.py:1215`): `pages = [-1, last line of
  page 1, …]`. Page capacity `linesOnPage * 10` minus headers, minus 20 for
  `CONTINUED:` and 10 for `(cont'd)` on later pages, never below 50.
  Break adjustment by type of the last line (`trelby/screenplay.py:1281-1359`,
  `removeDanglingElement` `trelby/screenplay.py:1370`).
  `lastPaginated` is set for the editor's timed re-pagination.
- `line2page`, `line2pageNoAdjust` (binary search,
  `trelby/screenplay.py:1556-1574`), `page2lines` (`trelby/screenplay.py:1595`),
  `getPageNumbers` (`trelby/screenplay.py:1605`), `needsMore`
  (`trelby/screenplay.py:1180`), `getPrevSpeaker` (`trelby/screenplay.py:1192`).

Editing commands (`cmd(name)` calls `<name>Cmd` then `cmdPost`,
`trelby/screenplay.py:2484`)
- Movement: `moveLeftCmd` … `moveSceneDownCmd`
  (`trelby/screenplay.py:2500-2669`). Up/Down move the completion selection
  when a list is open (`trelby/screenplay.py:2520-2545`).
- Text: `addCharCmd` (`trelby/screenplay.py:2846`), `deleteBackwardCmd`
  (`trelby/screenplay.py:2671`), `deleteForwardCmd`
  (`trelby/screenplay.py:2726`), `insertForcedLineBreakCmd`
  (`trelby/screenplay.py:2802`).
- Elements: `splitElementCmd` (Enter, `trelby/screenplay.py:2813`),
  `tabCmd` (`trelby/screenplay.py:2822`), `toPrevTypeTabCmd`
  (`trelby/screenplay.py:2836`), `to<Type>Cmd` (`trelby/screenplay.py:2951-2976`)
  → `convertTypeTo(lt, saveUndo)` (`trelby/screenplay.py:1397`, works on the
  selection's elements if any; empty parenthetical ↔ `()`).
- Selection and clipboard: `getMarkedLines`, `getMarkedColumns`,
  `getSelectedAsCD(doDelete)` (cut/copy, `trelby/screenplay.py:1873`),
  `paste(clines)` (`trelby/screenplay.py:1984`), `selectSceneCmd`,
  `selectAllCmd`. Neither cut nor copy puts a scene number on the
  clipboard, so a pasted scene has none; pasting several elements at the
  start of a heading leaves its number with the heading's text
  (`trelby/screenplay.py:2031`, `trelby/screenplay.py:2045-2047`). `joinLines` drops the number of the
  line joined in, unless the line it joins is empty and has none
  (`trelby/screenplay.py:1474-1475`).
- Other: `removeElementTypes(tdict, saveUndo)` (`trelby/screenplay.py:2415`),
  `findError(line)` (`trelby/screenplay.py:2150`), `getWord` (spell checker,
  `trelby/screenplay.py:1659`), `capitalizeNeeded`
  (`trelby/screenplay.py:2081`).
- Queries for reports and dialogs: `getSceneLocations`, `getSceneNames`,
  `getCharacterNames`, `getSceneNumber`, `getCharCount`
  (`trelby/screenplay.py:1148-1652`).

Undo (`trelby/screenplay.py:2979-3088`)
- Doubly linked list of `undo.*` objects. A new edit while inside the
  history cuts off the redo part (`trelby/screenplay.py:2998-3022`).
  History is trimmed from the oldest end once the estimate reaches
  5 000 000 bytes (`trelby/screenplay.py:3037-3050`).
- Merging: consecutive `addChar` (word-level, spaces join the preceding
  word), `deleteBackward`, `deleteForward` merge when the cursor is where
  the last step left it (`trelby/screenplay.py:2679-2684`,
  `trelby/screenplay.py:2876-2899`).

Export
- `generateText(doPages)` (`trelby/screenplay.py:195`), `generateHtml(includeNotes)`
  (`trelby/screenplay.py:229`), `getElementsAsList()` → `[(lt, text)]` with
  forced breaks as `\n` and export caps applied (`trelby/screenplay.py:321`),
  `generateFDX` (`trelby/screenplay.py:346`), `generateRTF`
  (`trelby/screenplay.py:395`); Fountain is written by `fountain.generate`,
  not here (`fountain.as-built.md`),
  `generatePDF(isExport)` / `generatePML(isExport)`
  (`trelby/screenplay.py:499-526`), `generatePMLPage(pager, pageNr, forPDF,
  doExtra)` (`trelby/screenplay.py:542`; `forPDF=False` is the screen
  layout, `doExtra=False` skips headers and styling and is used only for
  position queries; with `forPDF=True` Act break lines are not drawn and
  take no space, `trelby/screenplay.py:623-639`, so a PDF page ends a
  little short where it held one), `addSceneNumbers`
  (`trelby/screenplay.py:775`), `compareScripts(sp2) -> bytes | None`
  (`trelby/screenplay.py:2243`).

## Extension points

- **Element types.** A new type needs: a constant here
  (`trelby/screenplay.py:17-25`); a code character and name in
  `config._init` (`trelby/config.py:1766`); per-script defaults in
  `Config.__init__` (`trelby/config.py:445-512`); an Enter/Tab row in
  `ConfigGlobal.__init__` (`trelby/config.py:693-737`); a `ChangeTo<Type>`
  command in the alphabetical command list (`trelby/config.py:740`), a
  `cmdChangeTo<Type>` in `MyCtrl` (`trelby/trelbyctrl.py:1257-1285`) and a
  `to<Type>Cmd` here (`trelby/screenplay.py:2951-2976`); a menu id in
  `trelby/ids.py:72-92` and the right-click menu
  (`trelby/trelbyframe.py:289-297`); entries in the export maps `htmlMap`
  (`trelby/screenplay.py:233`), `xmlMap` (`trelby/screenplay.py:354`) and
  `trelby/fountain.py` (parse and generate); pagination rules if it should not end a page
  (`trelby/screenplay.py:1283-1359`); `findError` rules if it has sequencing
  constraints.
- **Enter/Tab behaviour** is data, not code: `splitElementCmd` / `tabCmd`
  read `cfgGl.getType(lt).newTypeEnter|newTypeTab` and
  `cfgGl.nextTypeTab(lt)` / `prevTypeTab(lt)`, the `tabOrder` cycle
  (`trelby/screenplay.py:2814`, `trelby/screenplay.py:2828-2833`,
  `trelby/screenplay.py:2842-2843`); the table is in
  `trelby/config.py:693-737`. `tabMakesNew` decides "new element vs.
  convert" (`trelby/screenplay.py:1708`).
- **Typing rules** (auto-capitalize, `INT.`/`EXT.` → Scene, `(` → Paren) are
  hard-coded in `addCharCmd` (`trelby/screenplay.py:2901-2938`) and
  `capitalizeNeeded` (`trelby/screenplay.py:2081`); only the two capitalize
  switches are settings.
- **Import** produces `lines` only; whatever imports must give lines that
  satisfy the invariants above before `reformatAll` + `paginate`
  (`trelby/trelbyctrl.py:253-255`).

## Gotchas

- `reformatAll` asserts there is no undo history
  (`trelby/screenplay.py:808`); `applyCfg` clears undo for that reason
  (`trelby/screenplay.py:178-181`).
- Element-type sequencing (Character → Dialogue, etc.) is **not enforced**
  while editing; only `findError` reports it, before export/print when
  `checkOnExport` is on.
- `Config.cursorLine` / `cursorColumn` and `cfgGl.honorSavedPos` are left
  from the `.trelby` format: nothing writes or reads the saved cursor now.
- Accepting a completion with End (`moveLineEndCmd`,
  `trelby/screenplay.py:2615-2630`) replaces only the current screen line's
  text, as Enter does, then re-wraps; it is one `SinglePara` undo step.
- `generateHtml` uses one `<pre>` per screen line, not per element
  (`trelby/screenplay.py:305-313`).
- `generateFDX` writes notes as an Action paragraph wrapping a `ScriptNote`,
  all with `ID="1"` (`trelby/screenplay.py:368-373`).

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
