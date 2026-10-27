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
(`trelby/trelbyctrl.py:53-122`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:286`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:111-122`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:535-548`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:129`: a name ending in
  `.trelby` is refused; anything else → `readFountain`,
  `trelby/trelbyctrl.py:151`: `fountain.load` on the UTF-8 bytes; errors
  through `loadError`, `trelby/trelbyctrl.py:163`),
  `saveFile(fileName)` (`trelby/trelbyctrl.py:173`: adds `.fountain` unless
  the name ends in it, `fountain.generate`; after writing, stores the new
  `fountainSource`, updates MRU and shows `showLost`,
  `trelby/trelbyctrl.py:192`, if some elements will not read back the
  same),
  `importFile(fileName)` (`trelby/trelbyctrl.py:205`; a `.fountain`, any
  case, is read by `readFountain` like Open and the tab stays untitled,
  `trelby/trelbyctrl.py:208-218`; other files by file-name ending to
  `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:230`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1124-1149`; Save As offers Fountain and All
  files), `OnRevertScript`
  (`trelby/trelbyctrl.py:812`), `canBeClosed` (`trelby/trelbyctrl.py:773`).
- `getExportable(action)` (`trelby/trelbyctrl.py:502`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1151`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:246-274`). `OnPrint` (`trelby/trelbyctrl.py:1203`); both make the PDF with
  `makePDF` (`trelby/trelbyctrl.py:1214`), which shows a `TrelbyError`
  (an unusable custom PDF font) and returns None.

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1399`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1242-1397`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1272-1282`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:792`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1341-1397`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:552-582`); `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:584`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:599-606`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:616`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:317-345`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1463`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1659`).
- Props: in an Action line, each word `propwords.find_prop_words` finds
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:1630-1639`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1614-1620`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:363-400`): scroll
  bar, status area (page, element, next Tab/Enter types), the tab's act
  panel (`trelby/trelbyctrl.py:391`, `trelby/actpanel.py:40`), Undo/Redo
  enable. `applyGlobalCfg` repaints every tab's act panel for a theme
  change (`trelby/trelbyctrl.py:434`).

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:833`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:889`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:853`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:903`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:403`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:411`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1222-1240`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:627-681`);
  watermark (`trelby/trelbyctrl.py:683`); find (`trelby/trelbyctrl.py:1030`),
  spell check (`trelby/trelbyctrl.py:1044`), delete elements
  (`trelby/trelbyctrl.py:1090`), goto scene/page
  (`trelby/trelbyctrl.py:949-1008`), find next error
  (`trelby/trelbyctrl.py:1013`).
- Reports (`trelby/trelbyctrl.py:690-708`) and compare
  (`trelby/trelbyctrl.py:710`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:115-122`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:427-431`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:453-476`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:478-491`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:220-233`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:616-644`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1160-1194`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- When `loadFile` fails, `MyFrame.openScript` has already made a new tab
  if the current one was touched (`trelby/trelbyframe.py:516-521`), so an
  empty tab stays open.
- `importFile` picks the importer by the lower-cased extension
  (`trelby/trelbyctrl.py:220`); anything not listed, a name without an
  extension included, is read as plain text.
- `OnCopySystem` lays text out with a fresh default `Screenplay`, so the
  formatted copy uses default element widths, not the script's
  (`trelby/trelbyctrl.py:858-866`). Bug: [bugs/editor/6](../initiatives/bugs/epics/editor/tasks/6-copy-system-default-widths.md).
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1607-1610`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys: all three compare against U+FFFD, so only "load
  `trelby/sample.fountain`" is reachable (`trelby/trelbyctrl.py:1423-1428`). Bug: [bugs/editor/10](../initiatives/bugs/epics/editor/tasks/10-test-hotkeys.md).
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:37-48`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
