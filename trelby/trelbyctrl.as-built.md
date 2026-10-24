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
  need it (`trelby/trelbyctrl.py:437-450`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:125`), `saveFile(fileName)`
  (`trelby/trelbyctrl.py:155`, adds `.trelby`, updates MRU),
  `importFile(fileName)` (`trelby/trelbyctrl.py:167`, dispatch by file-name
  ending to `myimport`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1014-1039`), `OnRevertScript`
  (`trelby/trelbyctrl.py:702`), `canBeClosed` (`trelby/trelbyctrl.py:663`).
- `getExportable(action)` (`trelby/trelbyctrl.py:404`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1041`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:197-225`). `OnPrint` (`trelby/trelbyctrl.py:1089`).

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1274`): see
  `../trelby.process.md`, stage 3. Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1117-1272`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1147-1157`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:682`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1216-1272`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:454-480`); `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:482`); `OnMouseWheel` moves
  the top line by `mouseWheelLines` (`trelby/trelbyctrl.py:497`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:506`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:268-296`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1338`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1523`).
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1489-1495`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:314-348`): scroll
  bar, status area (page, element, next Tab/Enter types), Undo/Redo enable.

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:723`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:779`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:743`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:793`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:351`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:359`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1097-1115`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:517-571`);
  watermark (`trelby/trelbyctrl.py:573`); find (`trelby/trelbyctrl.py:920`),
  spell check (`trelby/trelbyctrl.py:934`), delete elements
  (`trelby/trelbyctrl.py:980`), goto scene/page
  (`trelby/trelbyctrl.py:839-898`), find next error
  (`trelby/trelbyctrl.py:903`).
- Reports (`trelby/trelbyctrl.py:580-598`) and compare
  (`trelby/trelbyctrl.py:600`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:113-120`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:374-378`).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:169-182`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:614-639`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1050-1080`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- `loadFile` wraps `util.loadFile` in `str(...)`
  (`trelby/trelbyctrl.py:126`): a read error returns `None`, which becomes
  the string `"None"`, so the `None` check below never fires and the user
  gets a second error ("too few lines") from `Screenplay.load`.
- `importFile` unpacks `importFountain`'s result as a pair
  (`trelby/trelbyctrl.py:176-178`), but `importFountain` returns a bare
  `None` when the file cannot be read or is empty
  (`trelby/myimport.py:442-447`) → `TypeError`.
- `importFile` dispatches on `fileName.endswith("fdx")` etc. — no dot, case
  sensitive (`trelby/trelbyctrl.py:169-181`); `SCRIPT.FDX` is read as plain
  text.
- `OnInsertNbsp` (`trelby/trelbyctrl.py:900`), the character map and the
  name database feed `util.MyKeyEvent` into `OnKeyChar`, which calls
  `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1275`); `MyKeyEvent` has only
  `GetKeyCode` (`trelby/util.py:785`) → `AttributeError`.
- `OnCopySystem` lays text out with a fresh default `Screenplay`, so the
  formatted copy uses default element widths, not the script's
  (`trelby/trelbyctrl.py:748-756`).
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1482-1485`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys: all three compare against U+FFFD, so only "load
  `sample.trelby`" is reachable (`trelby/trelbyctrl.py:1298-1303`).
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:35-46`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
