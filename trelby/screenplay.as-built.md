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
    (`getTopLine` / `setTopLine` clamp it, `trelby/screenplay.py:882-889`);
  - `mark: Mark | None` — the other end of the selection;
  - `pages`, `pagesNoAdjust` — page table (see Pagination);
  - `acItems`, `acSel`, `acMax` — open auto-completion list;
  - `hasChanged`; `firstUndo` / `lastUndo` / `currentUndo` /
    `undoMemoryUsed` — undo chain;
  - `cfg: config.Config` (per script), `cfgGl` (shared global config),
    `titles`, `headers`, `locations`, `autoCompletion`, `scDict`.
- `Mark(line, column)` (`trelby/screenplay.py:3176`), `ClipData`
  (`lines`, `trelby/screenplay.py:3186`), `CommandState`
  (`doAutoComp` = `AC_DEL` / `AC_REDO` / `AC_KEEP`, `char`, `mark`,
  `needsVisifying`, `trelby/screenplay.py:3194`).

## Data-structure invariants

Checked by `_validate` (`trelby/screenplay.py:3137`, test code only):
- at least one line; cursor inside the script and inside its line;
- every line's text equals `util.toInputStr(text)`;
- `len(text.rstrip(" "))` ≤ the type's `width` — trailing spaces may run
  past the width (`trelby/screenplay.py:948-975`);
- an `LB_NONE` line does not end in a space;
- all lines of one element have the same type (an element ends at
  `LB_LAST`).

`_validate` checks them (`trelby/screenplay.py:3137`). Paragraph = lines up to `LB_FORCED` /
`LB_LAST`; element = lines up to `LB_LAST`; scene = from a `SCENE` or
`ACTBREAK` element to the next (`getSceneIndexesFromLine`,
`trelby/screenplay.py:1204`).

## Key functions

Settings
- `applyCfg(cfg)` replaces the script config, **clears undo**, re-wraps and
  re-paginates (`trelby/screenplay.py:176`).
- `__deepcopy__` is hand-written for speed and copies lines, config, titles,
  headers, locations, completion and dictionary, and the cursor — not undo
  history (`trelby/screenplay.py:155`).

Layout
- `wrapLine` (`trelby/screenplay.py:927`), `rewrapPara`
  (`trelby/screenplay.py:990`), `rewrapPrevPara`, `rewrapElem`
  (`trelby/screenplay.py:1057`), `reformatRange`
  (`trelby/screenplay.py:907`), `reformatAll` (`trelby/screenplay.py:891`).
  Parentheticals wrap one character narrower after their first line and are
  drawn one character further right (`needsExtraParenIndent`,
  `trelby/screenplay.py:131`).
- `getSpacingBefore(i)` — `beforeSpacing` at an element start, else
  `intraSpacing`, in tenths of a line (`trelby/screenplay.py:134`).

Pagination
- `paginate()` (`trelby/screenplay.py:1298`): `pages = [-1, last line of
  page 1, …]`. Page capacity `linesOnPage * 10` minus headers, minus 20 for
  `CONTINUED:` and 10 for `(cont'd)` on later pages, never below 50.
  Break adjustment by type of the last line (`trelby/screenplay.py:1364-1442`,
  `removeDanglingElement` `trelby/screenplay.py:1453`).
  `lastPaginated` is set for the editor's timed re-pagination.
- `line2page`, `line2pageNoAdjust` (binary search,
  `trelby/screenplay.py:1634-1652`), `page2lines` (`trelby/screenplay.py:1658`),
  `getPageNumbers` (`trelby/screenplay.py:1668`), `needsMore`
  (`trelby/screenplay.py:1263`), `getPrevSpeaker` (`trelby/screenplay.py:1275`).

Editing commands (`cmd(name)` calls `<name>Cmd` then `cmdPost`,
`trelby/screenplay.py:2538`)
- Movement: `moveLeftCmd` … `moveSceneDownCmd`
  (`trelby/screenplay.py:2554-2714`). Up/Down move the completion selection
  when a list is open (`trelby/screenplay.py:2574-2599`).
- Text: `addCharCmd` (`trelby/screenplay.py:2891`), `deleteBackwardCmd`
  (`trelby/screenplay.py:2716`), `deleteForwardCmd`
  (`trelby/screenplay.py:2771`), `insertForcedLineBreakCmd`
  (`trelby/screenplay.py:2847`).
- Elements: `splitElementCmd` (Enter, `trelby/screenplay.py:2858`),
  `tabCmd` (`trelby/screenplay.py:2867`), `toPrevTypeTabCmd`
  (`trelby/screenplay.py:2881`), `to<Type>Cmd` (`trelby/screenplay.py:2996-3021`)
  → `convertTypeTo(lt, saveUndo)` (`trelby/screenplay.py:1480`, works on the
  selection's elements if any; empty parenthetical ↔ `()`).
- Selection and clipboard: `getMarkedLines`, `getMarkedColumns`,
  `getSelectedAsCD(doDelete)` (cut/copy, `trelby/screenplay.py:1936`),
  `paste(clines)` (`trelby/screenplay.py:2047`), `selectSceneCmd`,
  `selectAllCmd`.
- Other: `removeElementTypes(tdict, saveUndo)` (`trelby/screenplay.py:2469`),
  `findError(line)` (`trelby/screenplay.py:2204`), `getWord` (spell checker,
  `trelby/screenplay.py:1722`), `capitalizeNeeded`
  (`trelby/screenplay.py:2135`).
- Queries for reports and dialogs: `getSceneLocations`, `getSceneNames`,
  `getCharacterNames`, `getSceneNumber`, `getCharCount`
  (`trelby/screenplay.py:1231-1715`).

Undo (`trelby/screenplay.py:3024-3133`)
- Doubly linked list of `undo.*` objects. A new edit while inside the
  history cuts off the redo part (`trelby/screenplay.py:3043-3067`).
  History is trimmed from the oldest end once the estimate reaches
  5 000 000 bytes (`trelby/screenplay.py:3082-3095`).
- Merging: consecutive `addChar` (word-level, spaces join the preceding
  word), `deleteBackward`, `deleteForward` merge when the cursor is where
  the last step left it (`trelby/screenplay.py:2724-2729`,
  `trelby/screenplay.py:2921-2944`).

Export
- `generateText(doPages)` (`trelby/screenplay.py:195`), `generateHtml(includeNotes)`
  (`trelby/screenplay.py:229`), `getElementsAsList()` → `[(lt, text)]` with
  forced breaks as `\n` and export caps applied (`trelby/screenplay.py:321`),
  `generateFDX` (`trelby/screenplay.py:346`), `generateFountain`
  (`trelby/screenplay.py:395`), `generateRTF` (`trelby/screenplay.py:492`),
  `generatePDF(isExport)` / `generatePML(isExport)`
  (`trelby/screenplay.py:596-623`), `generatePMLPage(pager, pageNr, forPDF,
  doExtra)` (`trelby/screenplay.py:639`; `forPDF=False` is the screen
  layout, `doExtra=False` skips headers and styling and is used only for
  position queries), `addSceneNumbers` (`trelby/screenplay.py:861`),
  `compareScripts(sp2) -> bytes | None` (`trelby/screenplay.py:2297`).

## Fountain export (`generateFountain`, `trelby/screenplay.py:395-489`)

- Title page: the first bold + centered string becomes `Title:` wrapped in
  `_**…**_`; a string whose first item is `by` becomes `Author:` from its
  third item on; a string starting with `Word:` keeps that key; anything else
  becomes `Contact:` (`trelby/screenplay.py:426-438`).
- A blank line is put before Scene, Action, Character, Transition, Shot,
  Act break and Note elements, never before Dialogue or Parenthetical
  (`trelby/screenplay.py:445-447`).
- Scene: `.` prefix unless the text starts with `INT`, `EXT`, `EST`,
  `INT./EXT`, `INT/EXT`, `I/E` or `I./E` (`trelby/screenplay.py:399`,
  `trelby/screenplay.py:450-454`).
- Action: an all-caps line gets two trailing spaces so it is not read as a
  Character (`trelby/screenplay.py:456-463`). Standard Fountain forces
  action with a leading `!`; the two-space form is what Trelby's importer
  recognizes (`trelby/myimport.py:679-680`).
- Transition: `> ` prefix unless it ends in `TO:`. Dialogue: empty lines
  become two spaces. Note: `[[…]]`. Act break: `>…<` (Fountain's centered
  text). Shot: two trailing spaces (`trelby/screenplay.py:465-485`).
- Not exported: screen/export styles (bold, italic, underline), headers,
  scene numbers, locations, page breaks.

## Extension points

- **Element types.** A new type needs: a constant here
  (`trelby/screenplay.py:17-25`); a code character and name in
  `config._init` (`trelby/config.py:1766`); per-script defaults in
  `Config.__init__` (`trelby/config.py:445-512`); an Enter/Tab row in
  `ConfigGlobal.__init__` (`trelby/config.py:693-737`); a `ChangeTo<Type>`
  command in the alphabetical command list (`trelby/config.py:740`), a
  `cmdChangeTo<Type>` in `MyCtrl` (`trelby/trelbyctrl.py:1206-1234`) and a
  `to<Type>Cmd` here (`trelby/screenplay.py:2996-3021`); a menu id in
  `trelby/ids.py:72-92` and the right-click menu
  (`trelby/trelbyframe.py:289-297`); entries in the export maps `htmlMap`
  (`trelby/screenplay.py:233`), `xmlMap` (`trelby/screenplay.py:354`) and the
  Fountain branches; pagination rules if it should not end a page
  (`trelby/screenplay.py:1366-1442`); `findError` rules if it has sequencing
  constraints.
- **Enter/Tab behaviour** is data, not code: `splitElementCmd` / `tabCmd`
  read `cfgGl.getType(lt).newTypeEnter|newTypeTab` and
  `cfgGl.nextTypeTab(lt)` / `prevTypeTab(lt)`, the `tabOrder` cycle
  (`trelby/screenplay.py:2859`, `trelby/screenplay.py:2873-2878`,
  `trelby/screenplay.py:2887-2888`); the table is in
  `trelby/config.py:693-737`. `tabMakesNew` decides "new element vs.
  convert" (`trelby/screenplay.py:1771`).
- **Typing rules** (auto-capitalize, `INT.`/`EXT.` → Scene, `(` → Paren) are
  hard-coded in `addCharCmd` (`trelby/screenplay.py:2946-2983`) and
  `capitalizeNeeded` (`trelby/screenplay.py:2135`); only the two capitalize
  switches are settings.
- **Fountain export**: `generateFountain` above; it works from
  `getElementsAsList()`, so it sees export caps but no styles.
- **Import** produces `lines` only; whatever imports must give lines that
  satisfy the invariants above before `reformatAll` + `paginate`
  (`trelby/trelbyctrl.py:222-226`).

## Gotchas

- `reformatAll` asserts there is no undo history
  (`trelby/screenplay.py:894`); `applyCfg` clears undo for that reason
  (`trelby/screenplay.py:178-181`).
- Element-type sequencing (Character → Dialogue, etc.) is **not enforced**
  while editing; only `findError` reports it, before export/print when
  `checkOnExport` is on.
- `Config.cursorLine` / `cursorColumn` and `cfgGl.honorSavedPos` are left
  from the `.trelby` format: nothing writes or reads the saved cursor now.
- Completing with End replaces the line text with no undo record and no
  re-wrap (`moveLineEndCmd`, `trelby/screenplay.py:2669-2675`). Bug: [bugs/editor/5](../initiatives/bugs/epics/editor/tasks/5-end-completion-no-undo.md).
- `generateFountain`: `kwPattern` is `^([A-za-z][^:]+:)` — the range `A-z`
  also matches `[ \ ] ^ _` and the backtick (`trelby/screenplay.py:427`);
  `looksLikeScene` is a bare prefix test, so an action or heading starting
  with e.g. `INTO` or `EXTRA` counts as a scene (`trelby/screenplay.py:402-409`);
  inside the Action branch it is called with the whole element text `txt`,
  so every line of an action element that starts like a heading gets the
  two trailing spaces (`trelby/screenplay.py:459`) — the trick Trelby's own
  Fountain importer reads back (`trelby/myimport.py:611-612`), not a
  Fountain rule; `titleLine.items[0]`
  raises `IndexError` on a title string with no items
  (`trelby/screenplay.py:433`). Bug: [bugs/import-export/4](../initiatives/bugs/epics/import-export/tasks/4-fountain-export-scene-guess.md), [bugs/import-export/5](../initiatives/bugs/epics/import-export/tasks/5-title-keyword-pattern.md), [bugs/import-export/6](../initiatives/bugs/epics/import-export/tasks/6-fountain-export-empty-title.md).
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
- **Not covered**: `save()` round-trip, `generateFountain`, `generateFDX`,
  `generateHtml`, `generateRTF`, `generateText`, `compareScripts`,
  `paginate` results, undo/redo. `tests/execute_random_tests.py` is a
  manual random-operation fuzzer, not part of the suite.
