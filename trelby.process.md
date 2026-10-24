# Trelby pipeline

Trelby is a wxPython screenplay editor. It keeps a script as a flat list of
wrapped lines, lays those lines out in pages with the same arithmetic the PDF
uses, and saves them in its own text format (`.trelby`). It imports six
foreign formats and exports six.

This file is the **stage-by-stage spec** of what the program does, in the
order a session runs. Per-module detail is in each folder's `CLAUDE.md` (and
`trelby/<module>.as-built.md` for the large modules). The user manual is
`doc/manual.xml`; the `.trelby` file format is described in
`trelby/fileformat.txt`.

Baseline: Trelby 2.4.16.2 (`trelby/misc.py:20`) as forked into
`mocap-writer`.

---

## Inputs

- **command line** — `trelby.py [--test] [--conf <file>] [script ...]`,
  parsed by `opts.init()` (`trelby/opts.py:8`). Every argument that is not a
  flag is a script to open.
- **global config** — `<confPath>/default.conf` (`trelby/globaldata.py:33`),
  `key:value` lines read into `config.ConfigGlobal`. `confPath` is
  `$XDG_CONFIG_HOME/trelby`, else `~/.trelby` if it exists, else
  `~/.config/trelby` (`trelby/misc.py:56-63`); `%USERPROFILE%\Trelby\conf` on
  Windows (`trelby/misc.py:70`).
- **window state** — `<confPath>/state` (`trelby/globaldata.py:34`): window
  position and size, view mode, recently used files.
- **global spell-checker dictionary** — `<confPath>/spell_checker_dictionary`
  (`trelby/globaldata.py:35`).
- **scripts** — `.trelby` files; foreign scripts through File → Import.
- **bundled data** — `trelby/dict_en.dat` (spell checker),
  `trelby/names.txt` (name database), `trelby/resources/` (icons, splash,
  quotes), `trelby/locales/` (gettext catalogs).

## Stage 0 — startup

- `trelby.py:6` calls `trelby.trelby.main()` (`trelby/trelby.py:142`).
- Importing `trelby/trelby.py` already loads the translation catalog
  (`trelby/trelby.py:34` → `translations.trelby_translations_load()`,
  `trelby/translations.py:10`). It picks the language from `$LANG`, falls back
  to the base language and then to `en`, and calls `gettext.install()`, which
  puts `_` into builtins. Every other module uses that builtin `_` without
  importing it.
- `main()` runs `opts.init()` (`trelby/trelby.py:143`), builds `MyApp` and
  enters the wx main loop (`trelby/trelby.py:145-147`).
- `MyApp.OnInit` (`trelby/trelby.py:39`), in order:
  1. refuses wxPython other than 4.x (`trelby/trelby.py:41`);
  2. `misc.init()` (`trelby/trelby.py:53`) sets the platform flags,
     `progPath` (the repository root, `trelby/misc.py:54`) and `confPath`,
     and creates `confPath`; `util.init()` (`trelby/trelby.py:54`) builds the
     character tables and the in-memory DC used to measure text;
  3. `GlobalData()` (`trelby/trelby.py:56`, `trelby/globaldata.py:17`) holds
     the paths, the MRU list and the three view-mode objects;
  4. `os.chdir(misc.progPath)` (`trelby/trelby.py:80`);
  5. **config load**: `ConfigGlobal()` + `setDefaults()`
     (`trelby/trelby.py:82-84`; `setDefaults` checks that the command list is
     alphabetical, picks the platform screen fonts and looks for a PDF
     viewer, `trelby/config.py:1326`). If `default.conf` exists it is loaded
     (`trelby/trelby.py:90`), otherwise the defaults are written out
     (`trelby/trelby.py:94`). `ConfigGui(cfgGl)` turns colors and font names
     into wx pens, brushes and fonts (`trelby/trelby.py:97`,
     `trelby/config.py:1386`);
  6. window state and view mode (`trelby/trelby.py:108-110`) and the global
     spell-checker dictionary (`trelby/trelby.py:116`);
  7. `MyFrame` is created and `init()` adds the first, empty tab
     (`trelby/trelby.py:118-120`); each command-line script is opened with
     `openScript` (`trelby/trelby.py:123`);
  8. `checkFonts()` warns if a screen font is not fixed-width
     (`trelby/trelby.py:132`, `trelby/trelbyframe.py:518`);
  9. **splash**: if `splashTime > 0` (default 3 s, `trelby/config.py:1130`) a
     `SplashWindow` is shown and closes itself on a one-shot timer
     (`trelby/trelby.py:135`, `trelby/splash.py:61-64`, `trelby/splash.py:106`).

## Stage 1 — main window and editor

- `MyFrame.__init__` (`trelby/trelbyframe.py:28`) builds the menus
  (`trelby/trelbyframe.py:50-189`), the vertical toolbar from the SVG icons in `trelby/resources/`
  (recolored for dark system themes, `trelby/trelbyframe.py:193-241`), the tab bar
  (`misc.MyTabCtrl`), the status area (`misc.MyStatus`) and the right-click
  menus (`trelby/trelbyframe.py:278-301`).
- Each open script is one tab: a `MyPanel` (`trelby/trelbypanel.py:7`)
  holding a `MyCtrl` editor widget (`trelby/trelbyctrl.py:49`) and a vertical
  scroll bar. `MyCtrl` owns one `Screenplay` (`self.sp`) and binds paint,
  mouse and key events (`trelby/trelbyctrl.py:58-67`).
- `createEmptySp()` (`trelby/trelbyctrl.py:100`) starts a script with the
  default title page and header (`trelby/titles.py:15`,
  `trelby/headers.py:16`).
- Menu commands go to `MyFrame.On<Name>`, which mostly forwards to the
  current tab's `MyCtrl.On<Name>` (e.g. `trelby/trelbyframe.py:603-607`).
- Status area: page `x / y`, current element type, and what Tab and Enter
  will produce next (`MyCtrl.updateCommon`, `trelby/trelbyctrl.py:324`).

## Stage 2 — the screenplay model

- A `Screenplay` (`trelby/screenplay.py:52`) is a flat list `lines` of
  `Line(lb, lt, text)` (`trelby/line.py:10`), plus the cursor (`line`,
  `column`), the selection (`mark`), the page table (`pages`) and the undo
  chain. It also owns per-script `config.Config` (`cfg`), `Titles`,
  `Headers`, `Locations`, `AutoCompletion` and a script spell-checker
  dictionary (`trelby/screenplay.py:53-108`).
- **Line types** (`trelby/screenplay.py:17-25`): `SCENE`, `ACTION`,
  `CHARACTER`, `DIALOGUE`, `PAREN`, `TRANSITION`, `SHOT`, `NOTE`, `ACTBREAK`.
  Each has a one-character code and a name in `config._init`
  (`trelby/config.py:1552`).
- **Line breaks** (`trelby/screenplay.py:6-14`): `LB_SPACE` (soft wrap at a
  space), `LB_NONE` (soft wrap inside a word), `LB_FORCED` (hard line break
  inside an element), `LB_LAST` (end of element). `LB_SPACE2` exists only to
  read old files.
- **Element** = consecutive lines up to and including an `LB_LAST` line; all
  its lines have the same type. **Paragraph** = lines up to an `LB_FORCED` or
  `LB_LAST`. **Scene** = the elements from one `SCENE` (or `ACTBREAK`)
  element to the next (`trelby/screenplay.py:1460`).
- **Wrapping**: `wrapLine` cuts text at the element type's width in
  characters (`trelby/screenplay.py:1183`); `rewrapPara` re-joins one
  paragraph and re-wraps it while keeping the cursor in place
  (`trelby/screenplay.py:1246`). `reformatAll` re-wraps the whole script and
  must not run while there is undo history (`trelby/screenplay.py:1147`).
- **Pages**: `paginate()` (`trelby/screenplay.py:1554`) fills
  `pages[i]` = index of the last line on page `i` (`pages[0] = -1`).
  Vertical space is counted in tenths of a line: each line is 10, plus the
  type's `beforeSpacing` / `intraSpacing`. Page capacity is
  `cfg.linesOnPage`, derived from paper height, margins and font size
  (`trelby/config.py:591-594`), minus header lines, `CONTINUED:` and
  `(cont'd)` lines. Breaks are moved back so that scene headings, shots and
  characters are not left at the bottom of a page and at least
  `pbActionLines` / `pbDialogueLines` lines of action / dialogue stay
  together (`trelby/screenplay.py:1622-1698`). `pagesNoAdjust` keeps the
  breaks before that adjustment.
- **Element-type sequencing rules** are only checked, not enforced, by
  `findError` (`trelby/screenplay.py:2460`): a character must be followed by
  a parenthetical or dialogue, a parenthetical must follow a character or
  dialogue, dialogue must follow a character or parenthetical.

## Stage 3 — editing and keyboard

- `MyCtrl.OnKeyChar` (`trelby/trelbyctrl.py:1274`) receives every key.
  - A printable character without Ctrl/Alt (`util.isValidInputChar`:
    code 32–255 minus 0x7F–0x9F and 0xAD, `trelby/util.py:206`) replaces the
    selection if `overwriteSelectionOnInsert` and is inserted with
    `Screenplay.addCharCmd` (`trelby/trelbyctrl.py:1281-1305`).
  - Anything else is looked up in `MyFrame.kbdCommands`
    (`trelby/trelbyframe.py:488-506`, built from `cfgGl.commands`,
    `trelby/config.py:687`). Menu commands call `MyFrame.On<Name>`; the rest
    call `MyCtrl.cmd<Name>` (`trelby/trelbyctrl.py:1312-1318`), which mostly
    forward to `Screenplay.<name>Cmd`.
  - After every command: `cmdPost` fixes the column and refreshes
    auto-completion (`trelby/screenplay.py:2783`); the script is re-paginated
    if `paginateInterval` seconds (default 1) have passed
    (`trelby/trelbyctrl.py:1325-1331`); the cursor line is scrolled into view
    and the screen is redrawn (`trelby/trelbyctrl.py:1333-1336`).
- **Enter** (`NewElement`, `trelby/config.py:943`) →
  `Screenplay.splitElementCmd` (`trelby/screenplay.py:3114`): splits the
  element at the cursor and gives the new element the current type's
  `newTypeEnter`. If an auto-completion list is open, the selected item
  replaces the line first (`trelby/screenplay.py:1848-1853`).
- **Tab** (`trelby/config.py:1085`) → `Screenplay.tabCmd`
  (`trelby/screenplay.py:3123`): at the end of a non-empty element (or before
  the closing `)` of a parenthetical) it creates a new element of type
  `newTypeTab` (`tabMakesNew`, `trelby/screenplay.py:2027`); otherwise it
  converts the current element to `nextTypeTab`. **Shift-Tab** converts to
  `prevTypeTab` (`trelby/screenplay.py:3137`).
- The Enter/Tab table is **global**, not per script: `ConfigGlobal.types`
  (`trelby/config.py:620-684`), one `TypeGlobal` per line type
  (`trelby/config.py:168`), editable in Settings → Elements.

  | current     | Enter      | Tab (new)  | Tab (convert) | Shift-Tab  |
  |-------------|------------|------------|---------------|------------|
  | Scene       | Action     | Character  | Action        | Transition |
  | Action      | Action     | Character  | Character     | Character  |
  | Character   | Dialogue   | Paren      | Action        | Action     |
  | Dialogue    | Character  | Action     | Paren         | Action     |
  | Paren       | Dialogue   | Action     | Character     | Dialogue   |
  | Transition  | Scene      | Transition | Scene         | Character  |
  | Shot        | Action     | Character  | Action        | Scene      |
  | Act break   | Scene      | Action     | Scene         | Scene      |
  | Note        | Action     | Character  | Action        | Character  |

- **Typing rules** in `addCharCmd` (`trelby/screenplay.py:3147`):
  - the first letter of a sentence is upper-cased when `capitalize` is on
    (`capitalizeNeeded`, `trelby/screenplay.py:2391`);
  - a lone `i` becomes `I` when `capitalizeI` is on
    (`trelby/screenplay.py:3208-3223`);
  - an element whose whole text becomes `INT.` or `EXT.` turns into a Scene
    (`trelby/screenplay.py:3229-3232`);
  - typing `(` as the only text of a Dialogue or Character element turns it
    into a Parenthetical `()` (`trelby/screenplay.py:3233-3239`).
- Element type changes: Alt+letter shortcuts (e.g. Alt+A Action,
  `trelby/config.py:711`) and the right-click menu call `convertTypeTo` (`trelby/screenplay.py:1736`, `trelby/trelbyctrl.py:75`).
- **Undo**: each edit records an `undo.*` object (`trelby/undo.py`) on a
  doubly linked list; consecutive typing and deleting are merged into word
  steps; history is trimmed past ~5 MB (`addUndo`,
  `trelby/screenplay.py:3298-3351`).
- **Auto-completion**: Scene, Character, Transition and Shot elements offer
  the matching earlier lines of the same type plus the configured list
  (`getMatchingText`, `trelby/screenplay.py:2078`).
- **Clipboard**: the internal clipboard keeps typed lines (`ClipData`,
  `trelby/screenplay.py:3442`); pasting from the system clipboard turns each
  non-empty text line into an Action element (`trelby/trelbyctrl.py:793`).

## Stage 4 — screen rendering (`viewmode`)

- `MyCtrl.OnPaint` (`trelby/trelbyctrl.py:1338`) asks the active view mode
  (`gd.vm`, `trelby/globaldata.py:106`) for `getScreen(ctrl, True, True)` →
  `(texts, dpages)`: positioned `TextString`s and, outside draft mode, page
  rectangles (`trelby/viewmode.py:82`). It then paints the workspace, pages,
  note boxes, selection, page-break lines, cursor, the text (one font per
  `TextString`) and the auto-completion popup.
- **Draft** (`ViewModeDraft`, `trelby/viewmode.py:202`): one endless page;
  each line is `fontYdelta` pixels (default 18) below the previous one plus
  its spacing; x comes from the element indent times the screen font's
  character width.
- **Layout** (`ViewModeLayout`, `trelby/viewmode.py:280`) and **side by
  side** (`ViewModeSideBySide`, `trelby/viewmode.py:422`): pages are built
  with `Screenplay.generatePMLPage(..., forPDF=False, ...)`
  (`trelby/screenplay.py:895`), the same code the PDF uses, and their
  millimeter positions are scaled to pixels by `ctrl.mm2p`
  (`trelby/trelbyctrl.py:116`).
- Screen fonts are the four global `font*` settings (`trelby/config.py:1172`)
  turned into `wx.Font`s by `ConfigGui` (`trelby/config.py:1449-1495`); the
  element's screen style (caps/bold/italic/underline) comes from the script's
  `Type.screen` (`trelby/config.py:131`). Colors are the global `*Color`
  settings (`trelby/config.py:1181-1228`).

## Stage 5 — save / open (`.trelby`)

- **Save**: `MyCtrl.saveFile` (`trelby/trelbyctrl.py:155`) forces the
  `.trelby` extension and writes `Screenplay.save()`
  (`trelby/screenplay.py:172`): BOM, `#Version 3`, the sections
  Auto-Completion, Config, Locations and Spell-Checker-Dict
  (`#Begin-X ` / `#End-X `, `key:value` lines), `#Title-String` /
  `#Title-Page` lines, `#Header-String` lines, `#Header-Empty-Lines`,
  `#Start-Script`, then one line per `Line`: line-break char + type char +
  text (`trelby/line.py:22`). UTF-8.
- **Open**: `MyFrame.openScript` (`trelby/trelbyframe.py:510`) reuses the
  current tab if it is untouched, else opens a new one, and calls
  `MyCtrl.loadFile` (`trelby/trelbyctrl.py:125`) → `Screenplay.load`
  (`trelby/screenplay.py:222`). Versions 1–3 are accepted; unknown line
  breaks become `LB_SPACE`, unknown types become Action, unknown config
  lines are skipped with a warning. After loading: restore the saved cursor
  if `honorSavedPos`, `reformatAll`, `paginate`, refresh locations
  (`trelby/screenplay.py:368-376`).
- **Revert** reloads from disk (`trelby/trelbyctrl.py:702`). **Close** asks
  before discarding changes (`trelby/trelbyctrl.py:663`). **Exit** writes the
  window state and removes temporary files (`trelby/trelbyframe.py:961`).

## Stage 6 — import (`myimport`)

- `MyFrame.OnImportScript` (`trelby/trelbyframe.py:609`) picks a file, reuses
  the tab if it is untouched, and calls `MyCtrl.importFile`
  (`trelby/trelbyctrl.py:167`), which dispatches **on the file name's
  ending**:
  - `fdx` → `importFDX` (`trelby/myimport.py:300`): Final Draft XML,
    `Content//Paragraph` by `Type`; script notes become Note elements;
  - `celtx` → `importCeltx` (`trelby/myimport.py:219`): the `script*` HTML
    inside the zip, `<p class=...>`;
  - `astx` → `importAstx` (`trelby/myimport.py:29`): Adobe Story XML;
  - `fountain` → `importFountain` (`trelby/myimport.py:395`): asks four
    options (title page, titles as action, strip markup, sections/synopses
    as notes), removes boneyard `/* */`, classifies each line, then merges
    lines of the same type into elements; it can fill the title page;
  - `fadein` → `importFadein` (`trelby/myimport.py:99`): `document.xml` in the
    zip (Open Screenplay Format);
  - anything else → `importTextFile` (`trelby/myimport.py:765`): plain text;
    groups lines by indentation, guesses a type per indent level, lets the
    user correct it in `ImportDlg` (`trelby/importdlg.py:8`).
- Every importer returns a list of `Line`s, or `None` on failure. The result
  replaces the tab's script, then `reformatAll` + `paginate`, and the script
  is marked modified with no file name (`trelby/trelbyctrl.py:187-194`).
- **There is no PDF import.**

## Stage 7 — export

- `MyCtrl.OnExportScript` (`trelby/trelbyctrl.py:1041`) first calls
  `getExportable` (`trelby/trelbyctrl.py:404`): optionally runs `findError`
  and asks whether to continue, drops Note elements on a copy when
  `pdfRemoveNotes`, re-paginates. The format is the file dialog's filter
  index:
  - **PDF** → `generatePDF` (`trelby/screenplay.py:852`) →
    `generatePML` (`trelby/screenplay.py:856`): title pages, then
    `generatePMLPage` per page (headers, `CONTINUED:`, `(MORE)`,
    `(cont'd)`, scene numbers, note outlines, TOC entries, line numbers),
    then custom PDF fonts → `pdf.generate` (`trelby/pdf.py:20`), which draws
    the PML with ReportLab;
  - **RTF** → `generateRTF` (`trelby/screenplay.py:748`), one style per
    element type;
  - **Final Draft XML** → `generateFDX` (`trelby/screenplay.py:602`);
  - **HTML** → `generateHtml` (`trelby/screenplay.py:485`), notes optional;
  - **Fountain** → `generateFountain` (`trelby/screenplay.py:651`): title
    page keys from the title strings, `.` forced scene headings, `>` forced
    transitions, `[[notes]]`, `>act break<`;
  - **formatted text** → `generateText` (`trelby/screenplay.py:451`), page
    markers optional.
- **Print** writes the same PDF to a temporary file and opens the configured
  PDF viewer (`trelby/trelbyctrl.py:1089`, `trelby/gutil.py:82`).
- **Watermark** writes one PDF per line of the watermark list, with that
  text and an optional common mark printed in light gray at 45° behind each
  page (`trelby/watermarkdlg.py:11`).
- **Compare scripts** diffs two open scripts' formatted text and shows the
  diff as a colored PDF (`trelby/trelbyctrl.py:600`,
  `trelby/screenplay.py:2553`).

## Stage 8 — reports

- Each report re-paginates and builds a PDF that is opened in the viewer
  (`trelby/trelbyctrl.py:580-598`, `trelby/reports.py`):
  - **script report** — line counts per type, interior/exterior share,
    longest/average scene and action length, speaking characters
    (`trelby/scriptreport.py:10`);
  - **scene report** — per scene: number, heading, length and, optionally,
    who speaks how many lines (`trelby/scenereport.py:9`);
  - **location report** — scenes grouped by the script's locations
    (`trelby/locationreport.py:11`);
  - **character report** — per speaking character: speeches, lines, words,
    pages and scenes (`trelby/characterreport.py:12`);
  - **dialogue chart** — per page, who speaks how much
    (`trelby/dialoguechart.py:14`).

## Other tools (menus)

Find & replace (`trelby/finddlg.py`), spell checker (`trelby/spellcheck.py`,
`trelby/spellcheckdlg.py`), character name database (`trelby/namesdlg.py`),
character map (`trelby/charmapdlg.py`), title pages (`trelby/titlesdlg.py`),
headers (`trelby/headersdlg.py`), locations (`trelby/locationsdlg.py`),
auto-completion lists (`trelby/autocompletiondlg.py`), global and script
settings (`trelby/cfgdlg.py` + `trelby/configpages/`), keyboard command list
(`trelby/commandsdlg.py`).
