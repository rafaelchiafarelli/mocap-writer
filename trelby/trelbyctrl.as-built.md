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
(`trelby/trelbyctrl.py:52-121`):
- `sp` — the `Screenplay`; `gd` — the shared `GlobalData`; `panel` — parent
  `MyPanel`.
- `fileName` (None for a new or imported script), `fileNameDisplay` (unique
  among open tabs: `name`, `name-2`, …, `trelby/trelbyctrl.py:240`).
- `chX`, `chY` — Courier character width and line height in mm at the
  script's font size; `pageW`, `pageH` — page size in pixels; `mm2p` —
  pixels per mm (`trelby/trelbyctrl.py:110-121`).
- `mouseSelectActive`; the find dialog's last settings `findDlg*`.
- Class attribute `screenBuf` — the double-buffer bitmap on platforms that
  need it (`trelby/trelbyctrl.py:484-497`).

## Key functions

Files
- `loadFile(fileName)` (`trelby/trelbyctrl.py:126`), `saveFile(fileName)`
  (`trelby/trelbyctrl.py:156`, adds `.trelby`, updates MRU),
  `importFile(fileName)` (`trelby/trelbyctrl.py:168`, dispatch by file-name
  ending to `myimport`; `.pdf`, any case, → `importPdf`,
  `trelby/trelbyctrl.py:182`), `OnSave` / `OnSaveScriptAs`
  (`trelby/trelbyctrl.py:1073-1098`), `OnRevertScript`
  (`trelby/trelbyctrl.py:761`), `canBeClosed` (`trelby/trelbyctrl.py:722`).
- `getExportable(action)` (`trelby/trelbyctrl.py:451`) → paginated script
  (a copy without notes if `pdfRemoveNotes`), after an optional error check.
- `OnExportScript` (`trelby/trelbyctrl.py:1100`) — format by the save
  dialog's filter index 0–5: PDF, RTF, FDX, HTML, Fountain, text;
  `getExportText` / `getExportHtml` ask their one option first
  (`trelby/trelbyctrl.py:200-228`). `OnPrint` (`trelby/trelbyctrl.py:1148`).

Keyboard
- `OnKeyChar(ev)` (`trelby/trelbyctrl.py:1333`): see
  `../trelby.process.md`, stage 3. The key code is `util.eventKeyCode(ev)`: the Unicode
  character, or the `WXK_` code for keys that have none (arrows, Home, End,
  F-keys). Plain characters go to `sp.addCharCmd`;
  other keys through `gd.mainFrame.kbdCommands` to `MyFrame.On<Name>` (menu
  commands) or `self.cmd<Name>(cs)`. Then `cmdPost`, timed re-pagination,
  scroll into view, `updateScreen`.
- `cmd<Name>` methods (`trelby/trelbyctrl.py:1176-1331`) are one-line
  forwards to `Screenplay`; `cmdDelete` / `cmdDeleteBackward` cut the
  selection instead when there is one (`trelby/trelbyctrl.py:1206-1216`);
  `cmdMovePageUp/Down` → `pageCmd` (`trelby/trelbyctrl.py:741`, also pages
  the completion list). `cmdSpeedTest` and `cmdTest` are developer hooks
  (`trelby/trelbyctrl.py:1275-1331`).

Mouse and scrolling
- `OnLeftDown` / `OnMotion` / `OnLeftUp` select with the mouse through
  `gd.vm.pos2linecol` (`trelby/trelbyctrl.py:501-531`); `OnLeftDown` first takes the keyboard
  focus, because wxGTK does not give it to this control on a click; `OnRightDown` shows
  the element-type menu (`trelby/trelbyctrl.py:533`); `OnMouseWheel` moves
  the top line by `mouseWheelLines`, or zooms in / out with Ctrl held
  (`trelby/trelbyctrl.py:548-555`); `OnScroll`
  follows the scroll bar (`trelby/trelbyctrl.py:565`).
- `makeLineVisible`, `isLineVisible`, `adjustScrollBar`
  (`trelby/trelbyctrl.py:271-299`).

Painting
- `OnPaint` (`trelby/trelbyctrl.py:1397`): workspace fill, then either one
  endless page (draft, `dpages` empty) or a rectangle + shadow per
  `DisplayPage`; per `TextString`: note box, selection, show-formatting
  marks, page-break lines (draft only, by `cfgGl.pbi`), cursor; then
  underlines and text; then `drawAutoComp` (`trelby/trelbyctrl.py:1593`).
- Props: in an Action line, each word `propwords.find_prop_words` finds
  in the line's own text (not the screen text, which is all caps when the
  Action style is) gets an underline of the text pen; display only
  (`trelby/trelbyctrl.py:1564-1573`). A line already underlined by its
  style gets no extra underline.
- Text color: `cfgGui.textColor`, or the per-type color when
  `useCustomElemColors`; header/continued texts (line −1) use
  `textHdrColor` (`trelby/trelbyctrl.py:1548-1554`).
- `updateScreen` / `updateCommon` (`trelby/trelbyctrl.py:317-352`): scroll
  bar, status area (page, element, next Tab/Enter types), Undo/Redo enable.

Clipboard
- `OnCut(doUpdate, doDelete, copyToClip)` (`trelby/trelbyctrl.py:782`),
  `OnCopy`, `OnPaste(clines)` (`trelby/trelbyctrl.py:838`) — the internal
  clipboard lives on the frame (`MyFrame.clipboard`).
- `OnCopySystem(formatted)` (`trelby/trelbyctrl.py:802`), `OnPasteSystemCb`
  (`trelby/trelbyctrl.py:852`, each non-empty line → one Action element).

Settings and dialogs
- `applyCfg(newCfg)` (`trelby/trelbyctrl.py:355`) — script settings;
  `applyGlobalCfg(newCfgGl, writeCfg)` (`trelby/trelbyctrl.py:363`) — global
  settings: rebuilds `ConfigGui`, keyboard table, every tab's cache, writes
  `default.conf`.
- `OnSettings` / `OnScriptSettings` (`trelby/trelbyctrl.py:1156-1174`)
  open `CfgDlg` on a deep copy; Apply and OK call the apply function.
- Script dialogs on deep copies, stored back on OK: auto-completion, titles,
  headers, locations, script dictionary (`trelby/trelbyctrl.py:576-630`);
  watermark (`trelby/trelbyctrl.py:632`); find (`trelby/trelbyctrl.py:979`),
  spell check (`trelby/trelbyctrl.py:993`), delete elements
  (`trelby/trelbyctrl.py:1039`), goto scene/page
  (`trelby/trelbyctrl.py:898-957`), find next error
  (`trelby/trelbyctrl.py:962`).
- Reports (`trelby/trelbyctrl.py:639-657`) and compare
  (`trelby/trelbyctrl.py:659`).

## Extension points

- **Colors** are read in `OnPaint` and `drawAutoComp` from `gd.cfgGui`
  pens/brushes/colours only; a new color is a `ConfigGlobal` color var plus
  its use here (`config.as-built.md`, Extension points).
- **Screen fonts / zoom**: `refreshCache` derives `pageW` and `mm2p` from
  the view mode's `getPageWidth` (`trelby/trelbyctrl.py:114-121`); any zoom
  has to change what `getPageWidth` / the fonts return and then call
  `refreshCache` on every tab, as `applyGlobalCfg` does
  (`trelby/trelbyctrl.py:379-383`). The zoom does exactly that:
  `OnZoomIn` / `OnZoomOut` / `OnZoomReset` change `cfgGl.zoom` and, if it
  changed, `applyZoom` rebuilds `ConfigGui`, refreshes every tab, updates
  the status area and writes the global config to `confFilename`
  (`trelby/trelbyctrl.py:402-425`). No re-pagination: the PDF layout does
  not change.
- **Theme from the menu**: `OnDarkTheme(dark)` (`trelby/trelbyctrl.py:427-440`)
  calls `cfgGl.setTheme`, rebuilds `ConfigGui`, repaints the frame (tab bar
  and status area use theme colors too) and writes the global config. GTK
  menus and dialogs only follow after a restart (`docker/run.sh` reads the
  theme at start).
- **Import formats**: one more `elif` on the file-name ending in
  `importFile` (`trelby/trelbyctrl.py:170-185`) plus the file-dialog
  wildcard in `MyFrame.OnImportScript` (`trelby/trelbyframe.py:620-648`).
- **Export formats**: one more filter in the wildcard and branch in
  `OnExportScript` (`trelby/trelbyctrl.py:1109-1139`); the branch order is
  the filter index.
- **New command**: a `Command` in `ConfigGlobal` (alphabetical) and either a
  `cmd<Name>` here or, with `isMenu=True`, an `On<Name>` on `MyFrame`.

## Gotchas

- `loadFile` wraps `util.loadFile` in `str(...)`
  (`trelby/trelbyctrl.py:127`): a read error returns `None`, which becomes
  the string `"None"`, so the `None` check below never fires and the user
  gets a second error ("too few lines") from `Screenplay.load`. Bug: [bugs/editor/4](../initiatives/bugs/epics/editor/tasks/4-loadfile-none.md).
- `importFile` unpacks `importFountain`'s result as a pair
  (`trelby/trelbyctrl.py:177-179`), but `importFountain` returns a bare
  `None` when the file cannot be read or is empty
  (`trelby/myimport.py:442-447`) → `TypeError`. Bug: [bugs/import-export/1](../initiatives/bugs/epics/import-export/tasks/1-fountain-import-none.md).
- `importFile` dispatches on `fileName.endswith("fdx")` etc. — no dot, case
  sensitive (only `.pdf` is matched with the dot and in any case) (`trelby/trelbyctrl.py:170-184`); `SCRIPT.FDX` is read as plain
  text. Bug: [bugs/import-export/3](../initiatives/bugs/epics/import-export/tasks/3-import-extension-match.md).
- `OnInsertNbsp` (`trelby/trelbyctrl.py:959`), the character map and the
  name database feed `util.MyKeyEvent` into `OnKeyChar`, whose
  `util.eventKeyCode` calls `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1334`,
  `trelby/util.py:210`); `MyKeyEvent` has only
  `GetKeyCode` (`trelby/util.py:798`) → `AttributeError`. Bug: [bugs/editor/1](../initiatives/bugs/epics/editor/tasks/1-insert-char-crash.md).
- `OnCopySystem` lays text out with a fresh default `Screenplay`, so the
  formatted copy uses default element widths, not the script's
  (`trelby/trelbyctrl.py:807-815`). Bug: [bugs/editor/6](../initiatives/bugs/epics/editor/tasks/6-copy-system-default-widths.md).
- `OnPaint` keys its per-font text batches by testing
  `fi.font not in texts`, where `texts` is a list of `(font, data)` tuples
  (`trelby/trelbyctrl.py:1541-1544`); the test is always true, so every
  string gets its own `DrawTextList` call. Output is correct, just slower.
- Test-mode hotkeys: all three compare against U+FFFD, so only "load
  `sample.trelby`" is reachable (`trelby/trelbyctrl.py:1357-1362`). Bug: [bugs/editor/10](../initiatives/bugs/epics/editor/tasks/10-test-hotkeys.md).
- `toolbarshown` and the `KC_CTRL_*` constants at the top
  (`trelby/trelbyctrl.py:36-47`) are unused, as are the same names in
  `trelby/trelby.py:20-31`.

## Tests

- None. `MyCtrl` needs a running wx app; the suite tests `Screenplay`
  directly. The import dispatch, export dispatch, painting and clipboard
  code have no automated coverage.
