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
(`trelby/trelbyctrl.py:57-134`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:523`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:123-134`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:781-794`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:141`: a name ending in
  `.trelby` is refused; after the open, `scenenumbers.report` problems
  are shown, never fixed, `trelby/trelbyctrl.py:162-172`; anything else → `readFountain`,
  `trelby/trelbyctrl.py:177`: `fountain.load` on the UTF-8 bytes, after
  `fountain.importOptions` when an import passes options; errors
  through `loadError`, `trelby/trelbyctrl.py:194`),
  `saveFile(fileName)` (`trelby/trelbyctrl.py:204`: adds `.fountain` unless
  the name ends in it, gives the scene numbers (`numberScenes`,
  `trelby/trelbyctrl.py:341`: `scenenumbers.prepareSave`; if it refuses,
  asks to renumber all, else the save is cancelled), `fountain.generate`; after writing, stores the new
  `fountainSource`, updates MRU, writes the film records of the tab's own
  film (`openFilm`, `trelby/trelbyctrl.py:241`: the open film whose
  script this tab holds, not the current tab's, bugs/editor/20; then
  `saveFilmSettings`, `renameFilmScenes`, `saveFilmAnnotations`,
  `trelby/trelbyctrl.py:248-295`) and shows `showLost`,
  `trelby/trelbyctrl.py:401`, if some elements will not read back the
  same); `setFile` tells the frame (`scriptFileChanged`), so the current
  tab's film follows a new file name,
  `OnRenumberScenes` (Script → Renumber all scenes, with a warning,
  `trelby/trelbyctrl.py:375`),
  `importFile(fileName)` → True when imported (`trelby/trelbyctrl.py:435`; a `.fountain`, any
  case, first asks the Import → Fountain options (`askFountainOptions`,
  `trelby/trelbyctrl.py:417`, front-matter/import/1: remove emphasis
  markup, sections and synopses as notes, title page lines as action,
  keep the title page; only the last ticked at first; Cancel imports
  nothing), then is read by `readFountain` with them and the tab stays untitled,
  `trelby/trelbyctrl.py:438-452`; other files by file-name ending to
  `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:464`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1484-1509`; Save As offers Fountain and All
  files), `OnRevertScript`
  (`trelby/trelbyctrl.py:1153`), `canBeClosed` (`trelby/trelbyctrl.py:1114`).
- `getExportable(action)` (`trelby/trelbyctrl.py:748`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1511`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:482-510`). `OnPrint` (`trelby/trelbyctrl.py:1563`); both make the PDF with
  `makePDF` (`trelby/trelbyctrl.py:1574`; for a film's script it first sets
  `sp.frontPages` to the film's front matter pages, front-matter/print/1), which shows a `TrelbyError`
  (an unusable custom PDF font) and returns None.

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1766`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1609-1764`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1635-1645`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:1133`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1704-1760`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:798-892`); two clicks select the word under the
  pointer and three or more the whole element (`OnLeftDClick`,
  `multiClick`, `trelby/trelbyctrl.py:833-854`, bugs/editor/14-16, fixed
  2026-10-28): wx reports no triple click, so a `clicks.ClickCounter`
  counts presses on the same line within 0.5 s; a double click on a space
  or punctuation selects the element; `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; a
  click on a scene number (`gd.vm.sceneNumberAt`) puts the cursor on the
  heading and shows `sceneNumberWarning` (`trelby/trelbyctrl.py:855`:
  numbers are permanent, with "do not show this again for the next 5
  clicks", `scenenumbers.clickWarning`) instead of selecting; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:912`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:927-934`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:944`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:554-582`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1832`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: a scene heading's hatch, the tint of
  annotated text and the margin mark where an annotation starts, when
  annotations are shown (`annotationMarks`, `trelby/trelbyctrl.py:315`,
  drawn at `trelby/trelbyctrl.py:1912`)
  (`cfgGui.sceneHatchBrush`, `trelby/trelbyctrl.py:1903`), note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:2056`).
- Props: in an Action line, each run `propwords.find_prop_words` finds
  (with the cursor's column on the cursor's line, so a run being typed is
  not underlined yet)
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:2020-2032`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:2004-2010`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:600-652`): first
  `scenenumbers.numberFinished` (`trelby/trelbyctrl.py:602`; a finished
  scene heading gets its number, fountain-native/scenes/6), then scroll
  bar, status area (page, element, next Tab/Enter types), the tab's act
  panel (`trelby/trelbyctrl.py:631`, `trelby/actpanel.py:40`), the bible
  panel's scene line (`BiblePanel.showScene`, `trelby/trelbyctrl.py:633-637`,
  film-bible/links/1), Undo/Redo enable. `applyGlobalCfg` repaints every tab's act panel for a theme
  change (`trelby/trelbyctrl.py:680`).

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:1174`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:1232`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:1194`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:1246`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:649`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:657`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1585-1603`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:955-1022`);
  watermark (`trelby/trelbyctrl.py:1024`); find (`trelby/trelbyctrl.py:1386`),
  spell check (`trelby/trelbyctrl.py:1400`), delete elements
  (`trelby/trelbyctrl.py:1450`), goto scene (a permanent number, `12.A`;
  a message when no scene has one yet) / page
  (`trelby/trelbyctrl.py:1292-1364`), find next error
  (`trelby/trelbyctrl.py:1369`).
- Reports (`trelby/trelbyctrl.py:1031-1049`) and compare
  (`trelby/trelbyctrl.py:1051`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:127-134`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:673-677`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:699-722`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:724-737`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:454-467`) plus the file-dialog
  wildcard in `MyFrame.askImportFile` (`trelby/trelbyframe.py:1095-1129`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1520-1554`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- When `loadFile` fails, `MyFrame.openScript` has already made a new tab
  if the current one was touched (`trelby/trelbyframe.py:594-599`), so an
  empty tab stays open.
- `importFile` picks the importer by the lower-cased extension
  (`trelby/trelbyctrl.py:454`); anything not listed, a name without an
  extension included, is read as plain text.
- `OnCopySystem` lays the selection out in a temporary `Screenplay` with a
  copy of the script's `Config`, so a formatted copy has the script's
  indents and styles (`trelby/trelbyctrl.py:1194-1230`); the lines arrive
  already wrapped by the script.
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1997-2000`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys (with `--test`): `å` loads `trelby/sample.fountain`,
  `¤` runs `cmdTest`, `½` `cmdSpeedTest`; written as `\xe5` / `\xa4` /
  `\xbd` escapes (`trelby/trelbyctrl.py:1786-1793`), the characters of
  upstream's 2006 code.
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:41-52`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
