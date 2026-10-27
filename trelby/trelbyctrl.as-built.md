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
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:283`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:110-121`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:532-545`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:128`: a name ending in
  `.trelby` is refused; anything else → `readFountain`,
  `trelby/trelbyctrl.py:150`: `fountain.load` on the UTF-8 bytes; errors
  through `loadError`, `trelby/trelbyctrl.py:162`),
  `saveFile(fileName)` (`trelby/trelbyctrl.py:172`: adds `.fountain` unless
  the name ends in it, `fountain.generate`; after writing, stores the new
  `fountainSource`, updates MRU and shows `showLost`,
  `trelby/trelbyctrl.py:191`, if some elements will not read back the
  same),
  `importFile(fileName)` (`trelby/trelbyctrl.py:204`; a `.fountain`, any
  case, is read by `readFountain` like Open and the tab stays untitled,
  `trelby/trelbyctrl.py:207-217`; other files by file-name ending to
  `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:227`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1121-1146`; Save As offers Fountain and All
  files), `OnRevertScript`
  (`trelby/trelbyctrl.py:809`), `canBeClosed` (`trelby/trelbyctrl.py:770`).
- `getExportable(action)` (`trelby/trelbyctrl.py:499`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1148`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:243-271`). `OnPrint` (`trelby/trelbyctrl.py:1200`).

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1385`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1228-1383`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1258-1268`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:789`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1327-1383`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:549-579`); `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:581`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:596-603`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:613`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:314-342`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1449`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1645`).
- Props: in an Action line, each word `propwords.find_prop_words` finds
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:1616-1625`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1600-1606`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:360-397`): scroll
  bar, status area (page, element, next Tab/Enter types), the tab's act
  panel (`trelby/trelbyctrl.py:388`, `trelby/actpanel.py:40`), Undo/Redo
  enable. `applyGlobalCfg` repaints every tab's act panel for a theme
  change (`trelby/trelbyctrl.py:431`).

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:830`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:886`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:850`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:900`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:400`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:408`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1208-1226`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:624-678`);
  watermark (`trelby/trelbyctrl.py:680`); find (`trelby/trelbyctrl.py:1027`),
  spell check (`trelby/trelbyctrl.py:1041`), delete elements
  (`trelby/trelbyctrl.py:1087`), goto scene/page
  (`trelby/trelbyctrl.py:946-1005`), find next error
  (`trelby/trelbyctrl.py:1010`).
- Reports (`trelby/trelbyctrl.py:687-705`) and compare
  (`trelby/trelbyctrl.py:707`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:114-121`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:424-428`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:450-473`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:475-488`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:219-230`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:616-644`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1157-1191`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- When `loadFile` fails, `MyFrame.openScript` has already made a new tab
  if the current one was touched (`trelby/trelbyframe.py:516-521`), so an
  empty tab stays open.
- `importFile` dispatches on `fileName.endswith("fdx")` etc. — no dot, case
  sensitive (only `.pdf` is matched with the dot and in any case) (`trelby/trelbyctrl.py:219-229`); `SCRIPT.FDX` is read as plain
  text. Bug: [bugs/import-export/3](../initiatives/bugs/epics/import-export/tasks/3-import-extension-match.md).
- `OnCopySystem` lays text out with a fresh default `Screenplay`, so the
  formatted copy uses default element widths, not the script's
  (`trelby/trelbyctrl.py:855-863`). Bug: [bugs/editor/6](../initiatives/bugs/epics/editor/tasks/6-copy-system-default-widths.md).
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1593-1596`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys: all three compare against U+FFFD, so only "load
  `trelby/sample.fountain`" is reachable (`trelby/trelbyctrl.py:1409-1414`). Bug: [bugs/editor/10](../initiatives/bugs/epics/editor/tasks/10-test-hotkeys.md).
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:36-47`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
