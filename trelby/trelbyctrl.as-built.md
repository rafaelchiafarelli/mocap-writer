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
(`trelby/trelbyctrl.py:54-123`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:364`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:112-123`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:622-635`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:130`: a name ending in
  `.trelby` is refused; after the open, `scenenumbers.report` problems
  are shown, never fixed, `trelby/trelbyctrl.py:151-161`; anything else → `readFountain`,
  `trelby/trelbyctrl.py:164`: `fountain.load` on the UTF-8 bytes; errors
  through `loadError`, `trelby/trelbyctrl.py:176`),
  `saveFile(fileName)` (`trelby/trelbyctrl.py:186`: adds `.fountain` unless
  the name ends in it, gives the scene numbers (`numberScenes`,
  `trelby/trelbyctrl.py:210`: `scenenumbers.prepareSave`; if it refuses,
  asks to renumber all, else the save is cancelled), `fountain.generate`; after writing, stores the new
  `fountainSource`, updates MRU and shows `showLost`,
  `trelby/trelbyctrl.py:270`, if some elements will not read back the
  same),
  `OnRenumberScenes` (Script → Renumber all scenes, with a warning,
  `trelby/trelbyctrl.py:244`),
  `importFile(fileName)` (`trelby/trelbyctrl.py:283`; a `.fountain`, any
  case, is read by `readFountain` like Open and the tab stays untitled,
  `trelby/trelbyctrl.py:286-296`; other files by file-name ending to
  `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:308`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1264-1289`; Save As offers Fountain and All
  files), `OnRevertScript`
  (`trelby/trelbyctrl.py:937`), `canBeClosed` (`trelby/trelbyctrl.py:898`).
- `getExportable(action)` (`trelby/trelbyctrl.py:589`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1291`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:324-352`). `OnPrint` (`trelby/trelbyctrl.py:1343`); both make the PDF with
  `makePDF` (`trelby/trelbyctrl.py:1354`), which shows a `TrelbyError`
  (an unusable custom PDF font) and returns None.

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1539`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1382-1537`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1412-1422`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:917`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1481-1537`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:639-707`); `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; a
  click on a scene number (`gd.vm.sceneNumberAt`) puts the cursor on the
  heading and shows `sceneNumberWarning` (`trelby/trelbyctrl.py:670`:
  numbers are permanent, with "do not show this again for the next 5
  clicks", `scenenumbers.clickWarning`) instead of selecting; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:709`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:724-731`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:741`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:395-423`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1605`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1801`).
- Props: in an Action line, each word `propwords.find_prop_words` finds
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:1772-1781`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1756-1762`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:441-493`): first
  `scenenumbers.numberFinished` (`trelby/trelbyctrl.py:443`; a finished
  scene heading gets its number, fountain-native/scenes/6), then scroll
  bar, status area (page, element, next Tab/Enter types), the tab's act
  panel (`trelby/trelbyctrl.py:472`, `trelby/actpanel.py:40`), the bible
  panel's scene line (`BiblePanel.showScene`, `trelby/trelbyctrl.py:474-478`,
  film-bible/links/1), Undo/Redo enable. `applyGlobalCfg` repaints every tab's act panel for a theme
  change (`trelby/trelbyctrl.py:521`).

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:958`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:1016`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:978`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:1030`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:490`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:498`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1362-1380`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:752-806`);
  watermark (`trelby/trelbyctrl.py:808`); find (`trelby/trelbyctrl.py:1170`),
  spell check (`trelby/trelbyctrl.py:1184`), delete elements
  (`trelby/trelbyctrl.py:1230`), goto scene (a permanent number, `12.A`;
  a message when no scene has one yet) / page
  (`trelby/trelbyctrl.py:1076-1148`), find next error
  (`trelby/trelbyctrl.py:1153`).
- Reports (`trelby/trelbyctrl.py:815-833`) and compare
  (`trelby/trelbyctrl.py:835`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:116-123`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:514-518`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:540-563`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:565-578`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:298-311`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:770-798`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1300-1334`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- When `loadFile` fails, `MyFrame.openScript` has already made a new tab
  if the current one was touched (`trelby/trelbyframe.py:553-558`), so an
  empty tab stays open.
- `importFile` picks the importer by the lower-cased extension
  (`trelby/trelbyctrl.py:298`); anything not listed, a name without an
  extension included, is read as plain text.
- `OnCopySystem` lays the selection out in a temporary `Screenplay` with a
  copy of the script's `Config`, so a formatted copy has the script's
  indents and styles (`trelby/trelbyctrl.py:978-1014`); the lines arrive
  already wrapped by the script.
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1749-1752`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys (with `--test`): `å` loads `trelby/sample.fountain`,
  `¤` runs `cmdTest`, `½` `cmdSpeedTest`; written as `\xe5` / `\xa4` /
  `\xbd` escapes (`trelby/trelbyctrl.py:1563-1570`), the characters of
  upstream's 2006 code.
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:38-49`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
