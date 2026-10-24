# trelbyctrl.py — as built

`trelby/trelbyctrl.py` (1601 lines) is `MyCtrl`, the wx widget that edits
one script. One instance per tab, inside a `MyPanel`
(`trelby/trelbypanel.py:22`). It owns the `Screenplay`, turns keys and mouse
events into `Screenplay` commands, paints the result through the active view
mode, and runs the file, dialog and report actions for its script. The
frame (`trelby/trelbyframe.py`) forwards most menu items to the current tab's
`MyCtrl`.

## State

Set in `__init__` / `clearVars` / `createEmptySp` / `refreshCache`
(`trelby/trelbyctrl.py:51-120`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:237`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:109-120`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:464-477`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:125`), `saveFile(fileName)`
  (`trelby/trelbyctrl.py:155`, adds `.trelby`, updates MRU),
  `importFile(fileName)` (`trelby/trelbyctrl.py:167`, dispatch by file-name
  ending to `myimport`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1049-1074`), `OnRevertScript`
  (`trelby/trelbyctrl.py:737`), `canBeClosed` (`trelby/trelbyctrl.py:698`).
- `getExportable(action)` (`trelby/trelbyctrl.py:431`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1076`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:197-225`). `OnPrint` (`trelby/trelbyctrl.py:1124`).

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1309`): see
  `../trelby.process.md`, stage 3. Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1152-1307`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1182-1192`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:717`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1251-1307`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:481-507`); `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:509`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:524-531`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:541`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:268-296`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1373`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1558`).
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1524-1530`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:314-348`): scroll
  bar, status area (page, element, next Tab/Enter types), Undo/Redo enable.

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:758`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:814`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:778`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:828`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:351`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:359`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1132-1150`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:552-606`);
  watermark (`trelby/trelbyctrl.py:608`); find (`trelby/trelbyctrl.py:955`),
  spell check (`trelby/trelbyctrl.py:969`), delete elements
  (`trelby/trelbyctrl.py:1015`), goto scene/page
  (`trelby/trelbyctrl.py:874-933`), find next error
  (`trelby/trelbyctrl.py:938`).
- Reports (`trelby/trelbyctrl.py:615-633`) and compare
  (`trelby/trelbyctrl.py:635`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:113-120`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:374-378`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:397-420`). No re-pagination: the PDF layout does
  not change.
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:169-182`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:617-642`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1085-1115`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- `loadFile` wraps `util.loadFile` in `str(...)`
  (`trelby/trelbyctrl.py:126`): a read error returns `None`, which becomes
  the string `"None"`, so the `None` check below never fires and the user
  gets a second error ("too few lines") from `Screenplay.load`. Bug: [bugs/editor/4](../initiatives/bugs/epics/editor/tasks/4-loadfile-none.md).
- `importFile` unpacks `importFountain`'s result as a pair
  (`trelby/trelbyctrl.py:176-178`), but `importFountain` returns a bare
  `None` when the file cannot be read or is empty
  (`trelby/myimport.py:442-447`) → `TypeError`. Bug: [bugs/import-export/1](../initiatives/bugs/epics/import-export/tasks/1-fountain-import-none.md).
- `importFile` dispatches on `fileName.endswith("fdx")` etc. — no dot, case
  sensitive (`trelby/trelbyctrl.py:169-181`); `SCRIPT.FDX` is read as plain
  text. Bug: [bugs/import-export/3](../initiatives/bugs/epics/import-export/tasks/3-import-extension-match.md).
- `OnInsertNbsp` (`trelby/trelbyctrl.py:935`), the character map and the
  name database feed `util.MyKeyEvent` into `OnKeyChar`, which calls
  `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1310`); `MyKeyEvent` has only
  `GetKeyCode` (`trelby/util.py:785`) → `AttributeError`. Bug: [bugs/editor/1](../initiatives/bugs/epics/editor/tasks/1-insert-char-crash.md).
- `OnCopySystem` lays text out with a fresh default `Screenplay`, so the
  formatted copy uses default element widths, not the script's
  (`trelby/trelbyctrl.py:783-791`). Bug: [bugs/editor/6](../initiatives/bugs/epics/editor/tasks/6-copy-system-default-widths.md).
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1517-1520`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys: all three compare against U+FFFD, so only "load
  `sample.trelby`" is reachable (`trelby/trelbyctrl.py:1333-1338`). Bug: [bugs/editor/10](../initiatives/bugs/epics/editor/tasks/10-test-hotkeys.md).
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:35-46`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
