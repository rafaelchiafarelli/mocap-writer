# Trelby pipeline

Trelby is a wxPython screenplay editor. It keeps a script as a flat list of
wrapped lines, lays those lines out in pages with the same arithmetic the PDF
uses, and opens and saves them as Fountain (`.fountain`). It imports seven
foreign formats (PDF through a layout profile) and exports six.

This file is the **stage-by-stage spec** of what the program does, in the
order a session runs. Per-module detail is in each folder's `CLAUDE.md` (and
`trelby/<module>.as-built.md` for the large modules). The user manual is
`doc/manual.xml`. Trelby's own `.trelby` format was removed (2026-10-25,
fountain-native/io/3 and io/4).

Baseline: Trelby 2.4.16.2 (`trelby/misc.py:20`) as forked into
`mocap-writer`.

---

## Inputs

- **command line** — `trelby.py [--test] [--conf <file>] [script ...]`,
  parsed by `opts.init()` (`trelby/opts.py:5`). Every argument that is not a
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
- **scripts** — `.fountain` files; foreign scripts through
  File → Import.
- **bundled data** — `trelby/dict_en.dat` (spell checker),
  `trelby/names.txt` (name database), `trelby/resources/` (icons, splash,
  quotes), `trelby/locales/` (gettext catalogs).

## Stage 0 — startup

- `trelby.py:6` calls `trelby.trelby.main()` (`trelby/trelby.py:148`).
- Importing `trelby/trelby.py` already loads the translation catalog
  (`trelby/trelby.py:34` → `translations.trelby_translations_load()`,
  `trelby/translations.py:10`). It picks the language from `$LANG`, falls back
  to the base language and then to `en`, and calls `gettext.install()`, which
  puts `_` into builtins. Every other module uses that builtin `_` without
  importing it.
- `main()` runs `opts.init()` (`trelby/trelby.py:149`), builds `MyApp` and
  enters the wx main loop (`trelby/trelby.py:151-153`).
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
     viewer, `trelby/config.py:1532`). If `default.conf` exists it is loaded
     (`trelby/trelby.py:90`), otherwise the defaults are written out
     (`trelby/trelby.py:94`). `ConfigGui(cfgGl)` turns colors and font names
     into wx pens, brushes and fonts (`trelby/trelby.py:97`,
     `trelby/config.py:1592`). The file dialogs start in the config's
     `scriptDir`, or in `$MOCAP_WRITER_WORK_DIR` when that is a directory
     (set by `docker/run.sh`, `trelby/trelby.py:102-108`);
  6. window state and view mode (`trelby/trelby.py:114-116`) and the global
     spell-checker dictionary (`trelby/trelby.py:122`);
  7. `MyFrame` is created and `init()` adds the first, empty tab
     (`trelby/trelby.py:124-126`); each command-line script is opened with
     `openScript` (`trelby/trelby.py:129`);
  8. `checkFonts()` warns if a screen font is not fixed-width
     (`trelby/trelby.py:138`, `trelby/trelbyframe.py:528`);
  9. **splash**: if `splashTime > 0` (default 3 s, `trelby/config.py:1205`) a
     `SplashWindow` is shown and closes itself on a one-shot timer
     (`trelby/trelby.py:141`, `trelby/splash.py:61-64`, `trelby/splash.py:106`).

## Stage 1 — main window and editor

- `MyFrame.__init__` (`trelby/trelbyframe.py:28`) builds the menus
  (`trelby/trelbyframe.py:50-194`), the vertical toolbar from the SVG icons in `trelby/resources/`
  (recolored for dark system themes, `trelby/trelbyframe.py:198-246`), the tab bar
  (`misc.MyTabCtrl`), the status area (`misc.MyStatus`) and the right-click
  menus (`trelby/trelbyframe.py:286-309`).
- Each open script is one tab: a `MyPanel` (`trelby/trelbypanel.py:7`)
  holding a `MyCtrl` editor widget (`trelby/trelbyctrl.py:52`), a vertical
  scroll bar and, at the right, the act panel (`trelby/actpanel.py:12`):
  the acts, their sizes in scenes and the cursor's act, untouched by zoom
  and scrolling (story-structure/acts/2). `MyCtrl` owns one `Screenplay` (`self.sp`) and binds paint,
  mouse and key events (`trelby/trelbyctrl.py:61-70`).
- `createEmptySp()` (`trelby/trelbyctrl.py:103`) starts a script with the
  default title page and header (`trelby/titles.py:13`,
  `trelby/headers.py:16`).
- Menu commands go to `MyFrame.On<Name>`, which mostly forwards to the
  current tab's `MyCtrl.On<Name>` (e.g. `trelby/trelbyframe.py:609-613`).
- Status area: page `x / y`, current element type, and what Tab and Enter
  will produce next (`MyCtrl.updateCommon`, `trelby/trelbyctrl.py:451`), and
  the zoom control `- 100 % +` (`trelby/misc.py:209-214`). The status area
  passes the keyboard focus back to the script when a click gives it focus
  (`MyFrame.OnStatusFocus`, `trelby/trelbyframe.py:841`).

## Stage 2 — the screenplay model

- A `Screenplay` (`trelby/screenplay.py:51`) is a flat list `lines` of
  `Line(lb, lt, text)` (`trelby/line.py:16`), plus the cursor (`line`,
  `column`), the selection (`mark`), the page table (`pages`) and the undo
  chain. It also owns per-script `config.Config` (`cfg`), `Titles`,
  `Headers`, `Locations`, `AutoCompletion` and a script spell-checker
  dictionary (`trelby/screenplay.py:52-116`).
- **Line types** (`trelby/screenplay.py:17-25`): `SCENE`, `ACTION`,
  `CHARACTER`, `DIALOGUE`, `PAREN`, `TRANSITION`, `SHOT`, `NOTE`, `ACTBREAK`.
  Each has a one-character code and a name in `config._init`
  (`trelby/config.py:1766`).
- **Line breaks** (`trelby/screenplay.py:6-14`): `LB_SPACE` (soft wrap at a
  space), `LB_NONE` (soft wrap inside a word), `LB_FORCED` (hard line break
  inside an element), `LB_LAST` (end of element). `LB_SPACE2` exists only to
  read old files.
- **Element** = consecutive lines up to and including an `LB_LAST` line; all
  its lines have the same type. **Paragraph** = lines up to an `LB_FORCED` or
  `LB_LAST`. **Scene** = the elements from one `SCENE` (or `ACTBREAK`)
  element to the next (`trelby/screenplay.py:1130`).
- **Wrapping**: `wrapLine` cuts text at the element type's width in
  characters (`trelby/screenplay.py:850`); `rewrapPara` re-joins one
  paragraph and re-wraps it while keeping the cursor in place
  (`trelby/screenplay.py:916`). `reformatAll` re-wraps the whole script and
  must not run while there is undo history (`trelby/screenplay.py:814`).
- **Pages**: `paginate()` (`trelby/screenplay.py:1212`) fills
  `pages[i]` = index of the last line on page `i` (`pages[0] = -1`).
  Vertical space is counted in tenths of a line: each line is 10, plus the
  type's `beforeSpacing` / `intraSpacing`. Page capacity is
  `cfg.linesOnPage`, derived from paper height, margins and font size
  (`trelby/config.py:650-653`), minus header lines, `CONTINUED:` and
  `(cont'd)` lines. Breaks are moved back so that scene headings, shots and
  characters are not left at the bottom of a page and at least
  `pbActionLines` / `pbDialogueLines` lines of action / dialogue stay
  together (`trelby/screenplay.py:1280-1356`). `pagesNoAdjust` keeps the
  breaks before that adjustment.
- **Element-type sequencing rules** are only checked, not enforced, by
  `findError` (`trelby/screenplay.py:2137`): a character must be followed by
  a parenthetical or dialogue, a parenthetical must follow a character or
  dialogue, dialogue must follow a character or parenthetical.

## Stage 3 — editing and keyboard

- `MyCtrl.OnKeyChar` (`trelby/trelbyctrl.py:1530`) receives every key, with the
    key code from `util.eventKeyCode` (`trelby/util.py:209`): the Unicode
    character, or the `WXK_` code for arrows, Home, End and other keys that
    have none. A key that matches no command is skipped, and GTK then uses an
    arrow to move the keyboard focus to another widget.
  - A printable character without Ctrl/Alt (`util.isValidInputChar`:
    code 32–255 minus 0x7F–0x9F and 0xAD, `trelby/util.py:219`) replaces the
    selection if `overwriteSelectionOnInsert` and is inserted with
    `Screenplay.addCharCmd` (`trelby/trelbyctrl.py:1537-1563`).
  - Anything else is looked up in `MyFrame.kbdCommands`
    (`trelby/trelbyframe.py:498-516`, built from `cfgGl.commands`,
    `trelby/config.py:740`). Menu commands call `MyFrame.On<Name>`; the rest
    call `MyCtrl.cmd<Name>` (`trelby/trelbyctrl.py:1570-1576`), which mostly
    forward to `Screenplay.<name>Cmd`.
  - After every command: `cmdPost` fixes the column and refreshes
    auto-completion (`trelby/screenplay.py:2460`); the script is re-paginated
    if `paginateInterval` seconds (default 1) have passed
    (`trelby/trelbyctrl.py:1583-1589`); the cursor line is scrolled into view
    and the screen is redrawn (`trelby/trelbyctrl.py:1591-1594`).
- **Enter** (`NewElement`, `trelby/config.py:996`) →
  `Screenplay.splitElementCmd` (`trelby/screenplay.py:2800`): splits the
  element at the cursor and gives the new element the current type's
  `newTypeEnter`. If an auto-completion list is open, the selected item
  replaces the line first (`trelby/screenplay.py:1511-1516`).
- **Tab** (`trelby/config.py:1138`) → `Screenplay.tabCmd`
  (`trelby/screenplay.py:2809`): at the end of a non-empty element (or before
  the closing `)` of a parenthetical) it creates a new element of type
  `newTypeTab` (`tabMakesNew`, `trelby/screenplay.py:1695`); otherwise it
  converts the current element to the next one of the Tab cycle.
  **Shift-Tab** converts to the previous one (`trelby/screenplay.py:2823`).
  The cycle is `ConfigGlobal.tabOrder`, Scene → Action → Character →
  Dialogue → Scene by default; an element outside it converts to Action
  both ways (`ConfigGlobal.nextTypeTab`, `trelby/config.py:1428-1444`).
- The Enter/Tab table and the cycle are **global**, not per script:
  `ConfigGlobal.types` (`trelby/config.py:691-737`), one `TypeGlobal` per
  line type (`trelby/config.py:228`), editable in Settings → Elements; the
  cycle only in the config file (`TabOrder`).

  | current     | Enter      | Tab (new)  | Tab (convert) | Shift-Tab  |
  |-------------|------------|------------|---------------|------------|
  | Scene       | Action     | Character  | Action        | Dialogue   |
  | Action      | Action     | Character  | Character     | Scene      |
  | Character   | Dialogue   | Paren      | Dialogue      | Action     |
  | Dialogue    | Character  | Action     | Scene         | Character  |
  | Paren       | Dialogue   | Action     | Action        | Action     |
  | Transition  | Scene      | Transition | Action        | Action     |
  | Shot        | Action     | Character  | Action        | Action     |
  | Act break   | Scene      | Action     | Action        | Action     |
  | Note        | Action     | Character  | Action        | Action     |

- **Typing rules** in `addCharCmd` (`trelby/screenplay.py:2833`):
  - the first letter of a sentence is upper-cased when `capitalize` is on
    (`capitalizeNeeded`, `trelby/screenplay.py:2068`);
  - a lone `i` becomes `I` when `capitalizeI` is on
    (`trelby/screenplay.py:2894-2909`);
  - an element whose whole text becomes `INT.` or `EXT.` turns into a Scene
    (`trelby/screenplay.py:2915-2918`);
  - typing `(` as the only text of a Dialogue or Character element turns it
    into a Parenthetical `()` (`trelby/screenplay.py:2919-2925`).
- Element type changes: Alt+letter shortcuts (e.g. Alt+A Action,
  `trelby/config.py:764`) and the right-click menu call `convertTypeTo` (`trelby/screenplay.py:1394`, `trelby/trelbyctrl.py:78`).
- **Undo**: each edit records an `undo.*` object (`trelby/undo.py`) on a
  doubly linked list; consecutive typing and deleting are merged into word
  steps; history is trimmed past ~5 MB (`addUndo`,
  `trelby/screenplay.py:2984-3037`).
- **Auto-completion**: Scene, Character, Transition and Shot elements offer
  the matching earlier lines of the same type plus the configured list
  (`getMatchingText`, `trelby/screenplay.py:1746`).
- **Clipboard**: the internal clipboard keeps typed lines (`ClipData`,
  `trelby/screenplay.py:3128`); pasting from the system clipboard turns each
  non-empty text line into an Action element (`trelby/trelbyctrl.py:1021`).

## Stage 4 — screen rendering (`viewmode`)

- `MyCtrl.OnPaint` (`trelby/trelbyctrl.py:1596`) asks the active view mode
  (`gd.vm`, `trelby/globaldata.py:106`) for `getScreen(ctrl, True, True)` →
  `(texts, dpages)`: positioned `TextString`s and, outside draft mode, page
  rectangles (`trelby/viewmode.py:90`). It then paints the workspace, pages,
  note boxes, selection, page-break lines, cursor, the text (one font per
  `TextString`) and the auto-completion popup.
- **Draft** (`ViewModeDraft`, `trelby/viewmode.py:225`): one endless page;
  each line is `fontYdelta` pixels (default 18) below the previous one plus
  its spacing; x comes from the element indent times the screen font's
  character width.
- **Layout** (`ViewModeLayout`, `trelby/viewmode.py:304`) and **side by
  side** (`ViewModeSideBySide`, `trelby/viewmode.py:448`): pages are built
  with `Screenplay.generatePMLPage(..., forPDF=False, ...)`
  (`trelby/screenplay.py:548`), the same code the PDF uses, and their
  millimeter positions are scaled to pixels by `ctrl.mm2p`
  (`trelby/trelbyctrl.py:119`).
- **Scene numbers** are shown left of each heading in every mode (and
  right of it in the page modes), in the header color: the permanent
  number, or in parentheses the one the next save will give (`(12.A)`),
  `?` when none fits (`scenenumbers.labels`). They are never part of the
  heading's text; a click on one shows a warning that numbers are
  permanent instead of placing the cursor in it
  (`MyCtrl.sceneNumberWarning`, fountain-native/scenes/4).
- Screen fonts are the four global `font*` settings (`trelby/config.py:1264`)
  turned into `wx.Font`s by `ConfigGui` (`trelby/config.py:1655-1706`); the
  element's screen style (caps/bold/italic/underline) comes from the script's
  `Type.screen` (`trelby/config.py:191`). In Action lines, words written
  fully in capitals (2+ letters, accents included) are underlined as props,
  on screen only (`propwords.find_prop_words`, `trelby/trelbyctrl.py:1763-1772`). **Zoom** (50–300 % in steps of
  10, Ctrl `+` / `-` / `0`, Ctrl + wheel, the status control) scales those
  fonts and the draft row height only; it is a global setting and never
  touches the PDF (`trelby/config.py:1697-1709`, `trelby/trelbyctrl.py:531`). Colors are the global `*Color`
  settings (`trelby/config.py:1273-1320`) of the chosen theme, Light or Dark
  (Settings → Colors, or the View → Dark theme check item, which switches
  at once and saves the config: `MyFrame.OnDarkTheme`,
  `trelby/trelbyframe.py:792-799`, `MyCtrl.OnDarkTheme`,
  `trelby/trelbyctrl.py:556-569`); each theme keeps its own colors
  (`trelby/config.py:1382-1411`). Under Docker, Dark also starts GTK's dark
  variant (`docker/run.sh:34-39`).

## Stage 5 — save / open (`.fountain`)

- **Fountain only** (fountain-native/io/3, 2026-10-25): Open and Save As
  offer Fountain and All files (`trelby/trelbyframe.py:594-607`,
  `trelby/trelbyctrl.py:1261-1280`); every file opened is read as
  Fountain, except a name ending in `.trelby`, which is refused with a
  message (`MyCtrl.loadFile`, `trelby/trelbyctrl.py:130-137`); Save adds
  `.fountain` unless the name ends in it (`MyCtrl.saveFile`,
  `trelby/trelbyctrl.py:186-206`). There is no `.trelby` reader or writer
  left (fountain-native/io/4).
- **Scene numbers before a save** (fountain-native/scenes/3,
  `MyCtrl.numberScenes`, `trelby/trelbyctrl.py:210`, →
  `scenenumbers.prepareSave`, `trelby/scenenumbers.py:354`): a number the
  script had at its open or last save and no longer on a heading comes
  back as an `OMITTED` heading at its place by number order (written as
  `.OMITTED #n#`); every scene without a number gets one by the rule; one
  undo step. A duplicate number or a scene with no room stops the save
  and offers Renumber all. **Script → Renumber all scenes** (with a
  warning) numbers every scene 1, 2, 3... and removes the `OMITTED`
  headings (`scenenumbers.renumberAll`, `trelby/scenenumbers.py:420`).
- **Save**: `fountain.generate(sp)` (`trelby/fountain.py:560`)
  writes unchanged elements, the title page and everything the editor does
  not show (boneyard, synopses, `##` sections, page breaks, blank lines)
  from the source read at open, and edited or new elements in canonical
  Fountain, so open → save → open is byte-identical. Elements Fountain
  cannot hold the way they are (e.g. dialogue with no character) are listed
  in a warning after the save (`MyCtrl.showLost`,
  `trelby/trelbyctrl.py:270`). Per-script settings are not written; page
  setup and styles can be kept with Script → Settings → Save as / Load.
  Detail: `trelby/fountain.as-built.md`.
- **Open**: `MyFrame.openScript` (`trelby/trelbyframe.py:520`) reuses the
  current tab if it is untouched, else opens a new one, and calls
  `MyCtrl.loadFile`: `readFountain` reads the file as bytes, decodes it as
  UTF-8 (else an error box, `trelby/trelbyctrl.py:164-174`) and builds it by
  `fountain.load` (`trelby/fountain.py:482`): elements and title page from
  the file, default headers and settings, `reformatAll`, `paginate`,
  refresh locations; its parsed source is kept in `sp.fountainSource` for
  the next save; each heading's `#n#` becomes its line's `num`. Problems
  with the scene numbers (duplicates, order, another tool's form, scenes
  with no number) are shown in a window, never fixed
  (`scenenumbers.report`, fountain-native/scenes/2). If the open fails, the
  new tab stays open, empty.
- **Revert** reloads from disk (`trelby/trelbyctrl.py:928`). **Close** asks
  before discarding changes (`trelby/trelbyctrl.py:889`). **Exit** with
  unsaved changes asks once; Save saves every modified tab, showing each
  (`MyFrame.saveAll`, `trelby/trelbyframe.py:1000`), and calls the exit off
  if one stays unsaved; then it writes the window state and removes
  temporary files (`trelby/trelbyframe.py:1013`).

## Stage 6 — import (`myimport`)

- `MyFrame.OnImportScript` (`trelby/trelbyframe.py:615`) picks a file, reuses
  the tab if it is untouched, and calls `MyCtrl.importFile`
  (`trelby/trelbyctrl.py:283`), which dispatches **on the file name's
  ending**:
  - `.fountain` (any case) → read like Open (`readFountain`, so
    `fountain.load`), but the tab stays untitled and marked modified
    (`trelby/trelbyctrl.py:286-296`, fountain-native/io/5);
  - `fdx` → `importFDX` (`trelby/myimport.py:299`): Final Draft XML,
    `Content//Paragraph` by `Type`; script notes become Note elements;
  - `celtx` → `importCeltx` (`trelby/myimport.py:218`): the `script*` HTML
    inside the zip, `<p class=...>`;
  - `astx` → `importAstx` (`trelby/myimport.py:28`): Adobe Story XML;
  - `fadein` → `importFadein` (`trelby/myimport.py:98`): `document.xml` in the
    zip (Open Screenplay Format);
  - `.pdf` (any case) → `importPdf` (`trelby/myimport.py:399`): asks
    nothing; `pdfimport.importPdf` detects the layout from the PDF (scene
    headings, cues, dialogue, page numbers, title page) and classifies each
    text line by its position. It never stops on a doubtful line: each
    issue becomes an `IMPORT:` note before the text it is about, and a
    report window lists the layout found and the issues. With
    `$MOCAP_WRITER_PDF_TRACE` set, a `.trace.tsv` of every decision is
    written there. Detail: `trelby/pdfimport.as-built.md`;
  - anything else → `importTextFile` (`trelby/myimport.py:434`): plain text;
    groups lines by indentation, guesses a type per indent level, lets the
    user correct it in `ImportDlg` (`trelby/importdlg.py:8`).
- Every other importer returns a list of `Line`s, or `None` on failure. The result
  replaces the tab's script, then `reformatAll` + `paginate`, and the script
  is marked modified with no file name (`trelby/trelbyctrl.py:316-321`).
- **PDF without the GUI:** `python -m trelby.pdfimport import <pdf>...
  --out <dir> [--profile <toml>] [--strict] [--trace]` writes one
  `.fountain` per PDF with `fountain.generate` (elements it cannot write
  so they read back the same go to stderr as `lost:` lines,
  `trelby/pdfimport.py:1151-1158`), issues as `[[IMPORT: …]]` notes;
  `probe <pdf>` lists
  the indents found and the layout detected (`trelby/pdfimport.py:1076`).

## Stage 7 — export

- `MyCtrl.OnExportScript` (`trelby/trelbyctrl.py:1282`) first calls
  `getExportable` (`trelby/trelbyctrl.py:580`): optionally runs `findError`
  and asks whether to continue, drops Note elements on a copy when
  `pdfRemoveNotes`, re-paginates. The format is the file dialog's filter
  index:
  - **PDF** → `generatePDF` (`trelby/screenplay.py:505`) →
    `generatePML` (`trelby/screenplay.py:509`): title pages, then
    `generatePMLPage` per page (headers, `CONTINUED:`, `(MORE)`,
    `(cont'd)`, scene numbers (the permanent ones, or `(12.A)` for a scene
    a save has not numbered yet; fountain-native/scenes/4), note
    outlines, TOC entries, line numbers);
    Act break lines are left out and the text after them moves up, with
    the pagination unchanged (`trelby/screenplay.py:638-654`,
    story-structure/acts/1),
    then custom PDF fonts → `pdf.generate` (`trelby/pdf.py:25`), which draws
    the PML with ReportLab;
  - **RTF** → `generateRTF` (`trelby/screenplay.py:401`), one style per
    element type;
  - **Final Draft XML** → `generateFDX` (`trelby/screenplay.py:352`);
  - **HTML** → `generateHtml` (`trelby/screenplay.py:235`), notes optional;
  - **Fountain** → `fountain.generate`, the same writer as Save
    (`trelby/trelbyctrl.py:1316-1322`); what it cannot write so it reads
    back the same is listed as on Save (`showLost`);
  - **formatted text** → `generateText` (`trelby/screenplay.py:201`), page
    markers optional.
- **Print** writes the same PDF to a temporary file and opens the configured
  PDF viewer, else the first one found (`xdg-open`, else `evince`, which the
  Docker image has; `trelby/util.py:1204-1220`) (`trelby/trelbyctrl.py:1334`, `trelby/gutil.py:82`). Export
  and Print make the PDF through `MyCtrl.makePDF`
  (`trelby/trelbyctrl.py:1345`): a custom PDF font that cannot be used is
  shown in a message box and nothing is written.
- **Watermark** writes one PDF per line of the watermark list, with that
  text and an optional common mark printed in light gray at 45° behind each
  page (`trelby/watermarkdlg.py:12`).
- **Compare scripts** diffs two open scripts' formatted text and shows the
  diff as a colored PDF (`trelby/trelbyctrl.py:826`,
  `trelby/screenplay.py:2230`).

## Stage 8 — reports

- Each report re-paginates and builds a PDF that is opened in the viewer
  (`trelby/trelbyctrl.py:806-824`, `trelby/reports.py`):
  - **script report** — line counts per type, interior/exterior share,
    longest/average scene and action length, speaking characters
    (`trelby/scriptreport.py:10`);
  - **scene report** — per scene: number, heading, length and, optionally,
    who speaks how many lines (`trelby/scenereport.py:10`);
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
