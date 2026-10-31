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
(`trelby/trelbyctrl.py:56-133`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:481`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:122-133`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:739-752`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:140`: a name ending in
  `.trelby` is refused; after the open, `scenenumbers.report` problems
  are shown, never fixed, `trelby/trelbyctrl.py:161-171`; anything else → `readFountain`,
  `trelby/trelbyctrl.py:174`: `fountain.load` on the UTF-8 bytes; errors
  through `loadError`, `trelby/trelbyctrl.py:186`),
  `saveFile(fileName)` (`trelby/trelbyctrl.py:196`: adds `.fountain` unless
  the name ends in it, gives the scene numbers (`numberScenes`,
  `trelby/trelbyctrl.py:323`: `scenenumbers.prepareSave`; if it refuses,
  asks to renumber all, else the save is cancelled), `fountain.generate`; after writing, stores the new
  `fountainSource`, updates MRU, writes the film records of the tab's own
  film (`openFilm`, `trelby/trelbyctrl.py:223`: the open film whose
  script this tab holds, not the current tab's, bugs/editor/20; then
  `saveFilmSettings`, `renameFilmScenes`, `saveFilmAnnotations`,
  `trelby/trelbyctrl.py:230-277`) and shows `showLost`,
  `trelby/trelbyctrl.py:383`, if some elements will not read back the
  same); `setFile` tells the frame (`scriptFileChanged`), so the current
  tab's film follows a new file name,
  `OnRenumberScenes` (Script → Renumber all scenes, with a warning,
  `trelby/trelbyctrl.py:357`),
  `importFile(fileName)` → True when imported (`trelby/trelbyctrl.py:397`; a `.fountain`, any
  case, is read by `readFountain` like Open and the tab stays untitled,
  `trelby/trelbyctrl.py:400-410`; other files by file-name ending to
  `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:422`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1425-1450`; Save As offers Fountain and All
  files), `OnRevertScript`
  (`trelby/trelbyctrl.py:1098`), `canBeClosed` (`trelby/trelbyctrl.py:1059`).
- `getExportable(action)` (`trelby/trelbyctrl.py:706`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1452`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:440-468`). `OnPrint` (`trelby/trelbyctrl.py:1504`); both make the PDF with
  `makePDF` (`trelby/trelbyctrl.py:1515`), which shows a `TrelbyError`
  (an unusable custom PDF font) and returns None.

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1700`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1543-1698`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1573-1583`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:1078`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1642-1698`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:756-850`); two clicks select the word under the
  pointer and three or more the whole element (`OnLeftDClick`,
  `multiClick`, `trelby/trelbyctrl.py:791-812`, bugs/editor/14-16, fixed
  2026-10-28): wx reports no triple click, so a `clicks.ClickCounter`
  counts presses on the same line within 0.5 s; a double click on a space
  or punctuation selects the element; `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; a
  click on a scene number (`gd.vm.sceneNumberAt`) puts the cursor on the
  heading and shows `sceneNumberWarning` (`trelby/trelbyctrl.py:813`:
  numbers are permanent, with "do not show this again for the next 5
  clicks", `scenenumbers.clickWarning`) instead of selecting; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:870`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:885-892`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:902`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:512-540`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1766`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: a scene heading's hatch, the tint of
  annotated text and the margin mark where an annotation starts, when
  annotations are shown (`annotationMarks`, `trelby/trelbyctrl.py:297`,
  drawn at `trelby/trelbyctrl.py:1850`)
  (`cfgGui.sceneHatchBrush`, `trelby/trelbyctrl.py:1841`), note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1990`).
- Props: in an Action line, each run `propwords.find_prop_words` finds
  (with the cursor's column on the cursor's line, so a run being typed is
  not underlined yet)
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:1958-1970`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1942-1948`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:558-610`): first
  `scenenumbers.numberFinished` (`trelby/trelbyctrl.py:560`; a finished
  scene heading gets its number, fountain-native/scenes/6), then scroll
  bar, status area (page, element, next Tab/Enter types), the tab's act
  panel (`trelby/trelbyctrl.py:589`, `trelby/actpanel.py:40`), the bible
  panel's scene line (`BiblePanel.showScene`, `trelby/trelbyctrl.py:591-595`,
  film-bible/links/1), Undo/Redo enable. `applyGlobalCfg` repaints every tab's act panel for a theme
  change (`trelby/trelbyctrl.py:638`).

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:1119`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:1177`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:1139`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:1191`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:607`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:615`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1523-1541`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:913-967`);
  watermark (`trelby/trelbyctrl.py:969`); find (`trelby/trelbyctrl.py:1331`),
  spell check (`trelby/trelbyctrl.py:1345`), delete elements
  (`trelby/trelbyctrl.py:1391`), goto scene (a permanent number, `12.A`;
  a message when no scene has one yet) / page
  (`trelby/trelbyctrl.py:1237-1309`), find next error
  (`trelby/trelbyctrl.py:1314`).
- Reports (`trelby/trelbyctrl.py:976-994`) and compare
  (`trelby/trelbyctrl.py:996`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:126-133`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:631-635`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:657-680`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:682-695`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:412-425`) plus the file-dialog
  wildcard in `MyFrame.askImportFile` (`trelby/trelbyframe.py:1087-1121`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1461-1495`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- When `loadFile` fails, `MyFrame.openScript` has already made a new tab
  if the current one was touched (`trelby/trelbyframe.py:592-597`), so an
  empty tab stays open.
- `importFile` picks the importer by the lower-cased extension
  (`trelby/trelbyctrl.py:412`); anything not listed, a name without an
  extension included, is read as plain text.
- `OnCopySystem` lays the selection out in a temporary `Screenplay` with a
  copy of the script's `Config`, so a formatted copy has the script's
  indents and styles (`trelby/trelbyctrl.py:1139-1175`); the lines arrive
  already wrapped by the script.
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1935-1938`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys (with `--test`): `å` loads `trelby/sample.fountain`,
  `¤` runs `cmdTest`, `½` `cmdSpeedTest`; written as `\xe5` / `\xa4` /
  `\xbd` escapes (`trelby/trelbyctrl.py:1724-1731`), the characters of
  upstream's 2006 code.
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:40-51`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
