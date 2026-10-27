# trelbyctrl.py — as built

`trelby/trelbyctrl.py` (1706 lines) is `MyCtrl`, the wx widget that edits
one script. One instance per tab, inside a `MyPanel`
(`trelby/trelbypanel.py:30`). It owns the `Screenplay`, turns keys and mouse
events into `Screenplay` commands, paints the result through the active view
mode, and runs the file, dialog and report actions for its script. The
frame (`trelby/trelbyframe.py`) forwards most menu items to the current tab's
`MyCtrl`.

## State

Set in `__init__` / `clearVars` / `createEmptySp` / `refreshCache`
(`trelby/trelbyctrl.py:52-121`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:270`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:110-121`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:519-532`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:128`: a name ending in
  `.trelby` is refused; anything else → `fountain.load` on the UTF-8 bytes;
  errors through `loadError`, `trelby/trelbyctrl.py:156`),
  `saveFile(fileName)` (`trelby/trelbyctrl.py:166`: adds `.fountain` unless
  the name ends in it, `fountain.generate`; after writing, stores the new
  `fountainSource`, updates MRU and shows `showLost`,
  `trelby/trelbyctrl.py:185`, if some elements will not read back the
  same),
  `importFile(fileName)` (`trelby/trelbyctrl.py:198`, dispatch by file-name
  ending to `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:212`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1108-1133`; Save As offers Fountain and All
  files), `OnRevertScript`
  (`trelby/trelbyctrl.py:796`), `canBeClosed` (`trelby/trelbyctrl.py:757`).
- `getExportable(action)` (`trelby/trelbyctrl.py:486`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1135`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:230-258`). `OnPrint` (`trelby/trelbyctrl.py:1183`).

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1368`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1211-1366`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1241-1251`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:776`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1310-1366`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:536-566`); `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:568`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:583-590`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:600`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:301-329`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1432`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1628`).
- Props: in an Action line, each word `propwords.find_prop_words` finds
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:1599-1608`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1583-1589`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:347-384`): scroll
  bar, status area (page, element, next Tab/Enter types), the tab's act
  panel (`trelby/trelbyctrl.py:375`, `trelby/actpanel.py:40`), Undo/Redo
  enable. `applyGlobalCfg` repaints every tab's act panel for a theme
  change (`trelby/trelbyctrl.py:418`).

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:817`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:873`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:837`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:887`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:387`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:395`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1191-1209`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:611-665`);
  watermark (`trelby/trelbyctrl.py:667`); find (`trelby/trelbyctrl.py:1014`),
  spell check (`trelby/trelbyctrl.py:1028`), delete elements
  (`trelby/trelbyctrl.py:1074`), goto scene/page
  (`trelby/trelbyctrl.py:933-992`), find next error
  (`trelby/trelbyctrl.py:997`).
- Reports (`trelby/trelbyctrl.py:674-692`) and compare
  (`trelby/trelbyctrl.py:694`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:114-121`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:411-415`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:437-460`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:462-475`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:200-215`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:616-644`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1144-1174`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- When `loadFile` fails, `MyFrame.openScript` has already made a new tab
  if the current one was touched (`trelby/trelbyframe.py:516-521`), so an
  empty tab stays open.
- `importFile` unpacks `importFountain`'s result as a pair
  (`trelby/trelbyctrl.py:207-209`), but `importFountain` returns a bare
  `None` when the file cannot be read or is empty
  (`trelby/myimport.py:442-447`) → `TypeError`. Bug: [bugs/import-export/1](../initiatives/bugs/epics/import-export/tasks/1-fountain-import-none.md).
- `importFile` dispatches on `fileName.endswith("fdx")` etc. — no dot, case
  sensitive (only `.pdf` is matched with the dot and in any case) (`trelby/trelbyctrl.py:200-214`); `SCRIPT.FDX` is read as plain
  text. Bug: [bugs/import-export/3](../initiatives/bugs/epics/import-export/tasks/3-import-extension-match.md).
- `OnInsertNbsp` (`trelby/trelbyctrl.py:994`), the character map and the
  name database feed `util.MyKeyEvent` into `OnKeyChar`, whose
  `util.eventKeyCode` calls `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1369`,
  `trelby/util.py:210`); `MyKeyEvent` has only
  `GetKeyCode` (`trelby/util.py:798`) → `AttributeError`. Bug: [bugs/editor/1](../initiatives/bugs/epics/editor/tasks/1-insert-char-crash.md).
- `OnCopySystem` lays text out with a fresh default `Screenplay`, so the
  formatted copy uses default element widths, not the script's
  (`trelby/trelbyctrl.py:842-850`). Bug: [bugs/editor/6](../initiatives/bugs/epics/editor/tasks/6-copy-system-default-widths.md).
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1576-1579`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys: all three compare against U+FFFD, so only "load
  `trelby/sample.fountain`" is reachable (`trelby/trelbyctrl.py:1392-1397`). Bug: [bugs/editor/10](../initiatives/bugs/epics/editor/tasks/10-test-hotkeys.md).
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:36-47`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
