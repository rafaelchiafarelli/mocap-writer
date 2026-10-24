# trelby — the application package: screenplay model, wx editor, import/export, reports

**Role:** All of Trelby's code. One flat package of 55 modules: the
screenplay model (`screenplay`, `line`, `undo`), configuration (`config`,
`mypickle`), the wx editor (`trelbyframe` → `trelbypanel` → `trelbyctrl`,
drawn by `viewmode`), the page language and PDF writer (`pml`, `pdf`), import
(`myimport`), reports and dialogs. Stage-by-stage behaviour is in
`../trelby.process.md`.

**Entry points:**
- `trelby.main()` (`trelby/trelby.py:142`) — the GUI program; called by
  `../trelby.py`.
- `screenplay.Screenplay.load(s, cfgGl)` / `.save()` — the `.trelby` format
  without any GUI (what the tests use, `tests/u.py`).
- `myimport.import*(fileName, frame)` — one function per import format.
- `Screenplay.generate{PDF,RTF,FDX,Html,Fountain,Text}` — exports.

**Inputs → Outputs:** `.trelby` scripts, imported `.fdx` / `.celtx` /
`.astx` / `.fountain` / `.fadein` / text files, and the config files under
`misc.confPath` → an edited script saved as `.trelby`, exports (PDF, RTF,
FDX, HTML, Fountain, text), report PDFs, and the global config and state
files.

## Files

Model and file format
- `screenplay.py` — `Screenplay`: the script as a flat list of `Line`s, the
  cursor, selection, pagination, every editing command, undo chain, `.trelby`
  load/save and all exports; also the `LB_*` and line-type constants. Detail:
  [screenplay.as-built.md](screenplay.as-built.md).
- `line.py` — `Line(lb, lt, text)` (`trelby/line.py:10`); `str(line)` is the
  saved form, line-break char + type char + text (`trelby/line.py:22`).
  `fromStr` has no error checking and is for internal storage only (undo).
- `undo.py` — undo objects: `FullCopy`, `SinglePara`, `ManyElems`,
  `AnyDifference` (`trelby/undo.py:167-264`); lines are stored as
  zlib-compressed strings when that is shorter (`trelby/undo.py:62`). The
  table at `trelby/undo.py:5-30` says which command uses which.
- `titles.py` — `Titles` (list of title pages) and `TitleString` (lines of
  text at an x/y position in mm, font, style); PML, RTF and the
  `#Title-String` save form (`trelby/titles.py:207`).
- `headers.py` — `Headers` / `HeaderString`: per-page header lines,
  `${PAGE}` replaced by the page number (`trelby/headers.py:90`); default is
  `${PAGE}.` right-aligned on line 1 (`trelby/headers.py:16`).
- `locations.py` — `Locations`: groups of scene headings that are the same
  place, used by the location report; `refresh` drops unknown headings
  (`trelby/locations.py:53`).
- `autocompletion.py` — `AutoCompletion`: per-script completion lists for
  Scene, Character, Transition (13 defaults) and Shot
  (`trelby/autocompletion.py:13-39`).
- `autocompletiontype.py` — `AutoCompletionType`: one element type's
  `enabled` flag and item list.
- `fileformat.txt` — the `.trelby` format description (sections, config
  keys, line codes).
- `sample.trelby` — sample script, loaded by a test-mode hotkey
  (`trelby/trelbyctrl.py:1298`).

Configuration
- `config.py` — `Config` (per script: element widths/indents/spacing and
  styles, paper, PDF options, strings), `ConfigGlobal` (Enter/Tab table,
  keyboard commands, colors, screen fonts, editor behaviour), `ConfigGui`
  (wx objects made from `ConfigGlobal`), line-type/line-break code tables.
  Detail: [config.as-built.md](config.as-built.md).
- `mypickle.py` — `Vars` and the `*Var` classes: typed settings with
  default, min/max and a save name, serialized as `name:value` lines
  (`trelby/mypickle.py:69-85`). Used by every saved object.
- `opts.py` — command-line options: `--test`, `--conf <file>`, script
  names (`trelby/opts.py:8`).
- `globaldata.py` — `GlobalData`: config file paths, MRU list, window
  geometry and view mode (saved to `state`), the three view-mode objects,
  the global spell-checker dictionary (`trelby/globaldata.py:17`).

Application and editor (wx)
- `trelby.py` — `MyApp.OnInit` (startup sequence, `trelby/trelby.py:39`)
  and `main()`; loads translations at import time (`trelby/trelby.py:34`).
- `trelbyframe.py` — `MyFrame`: menus, toolbar, tabs, status area;
  `On<Command>` handlers for every menu item, mostly forwarding to the
  current `MyCtrl`; open/import into a tab; exit (`trelby/trelbyframe.py:26`).
- `trelbypanel.py` — `MyPanel`: one tab = `MyCtrl` + vertical scroll bar
  (`trelby/trelbypanel.py:7`).
- `trelbyctrl.py` — `MyCtrl`: the editor widget for one script; key
  handling, mouse, painting, load/save/import/export/print, dialogs and
  reports for its script. Detail: [trelbyctrl.as-built.md](trelbyctrl.as-built.md).
- `viewmode.py` — the three screen layouts (draft, layout, side by side):
  where each line is drawn and which line/column a mouse position hits.
  Detail: [viewmode.as-built.md](viewmode.as-built.md).
- `ids.py` — wx menu ids and `idToLTMap` (right-click "Element type" ids →
  line types, `trelby/ids.py:81`).
- `misc.py` — platform flags, `progPath` / `confPath` (`misc.init`,
  `trelby/misc.py:23`), `version` (`trelby/misc.py:20`), and shared widgets:
  `MyTabCtrl` (tab bar, `trelby/misc.py:248`), `MyStatus`
  (`trelby/misc.py:156`), `MyFSButton`, `CheckBoxDlg`
  (`trelby/misc.py:722`), `ScriptChooserDlg`, `TextDlg`, `TextInputDlg`,
  `KeyDlg`, `MRUFiles` (`trelby/misc.py:1025`).
- `gutil.py` — GUI helpers: listbox select/add, stock buttons,
  `showTempPDF` (temp file + viewer, `trelby/gutil.py:82`).
- `util.py` — text and number helpers, the text-measuring DC, `Key`
  (keyboard shortcut ↔ int, `trelby/util.py:802`), file load/write
  (`trelby/util.py:981-1067`), PDF viewer lookup and launch
  (`trelby/util.py:1182-1243`).
- `error.py` — `TrelbyError`, `ConfigError`, `MiscError`.
- `translations.py` — `trelby_translations_load()`: picks the gettext
  catalog in `locales/` from `$LANG` and installs `_` as a builtin
  (`trelby/translations.py:10`).
- `splash.py` — `SplashWindow`: logo, version, random quote from
  `resources/quotes.txt`; closes on click or after `splashTime` seconds
  (`trelby/splash.py:61-64`); also the About box (`delay = -1`).

Page language and PDF
- `pml.py` — PML ("Page Modeling Language"): `Document` → `Page` → draw ops
  `TextOp`, `LineOp`, `RectOp`, `QuarterCircleOp`, `PDFOp`; all positions in
  mm from the top-left (`trelby/pml.py:38-245`). `TextFormatter` lays out
  plain report text into pages (`trelby/pml.py:250`).
- `pdf.py` — `generate(doc)`: draws a PML document with ReportLab, one
  `PDF*Op` per PML op, custom TrueType fonts, TOC outline. Detail:
  [pdf.as-built.md](pdf.as-built.md).
- `mypager.py` — `Pager`: the PML document being built plus scene counters
  shared across `generatePMLPage` calls (`trelby/mypager.py:6`).
- `fontinfo.py` — PDF core-font metrics: Courier (fixed 600 units), and
  256-entry width tables for Helvetica and Times (`getMetrics`,
  `trelby/fontinfo.py:11`).
- `truetype.py` — minimal TrueType/OpenType parser: PostScript name and
  embedding permission, used to validate custom PDF fonts
  (`trelby/configpages/pdffontspanel.py:156`).

Import
- `myimport.py` — importers for Adobe Story, Fade In, Celtx, Final Draft,
  Fountain and indented plain text. Detail:
  [myimport.as-built.md](myimport.as-built.md).
- `importdlg.py` — `ImportDlg`: lets the user set the element type of each
  indentation level found in a text file (`trelby/importdlg.py:8`).
- `indent.py` — `Indent`: statistics for one indentation level of a text
  file (`trelby/indent.py:2`).

Reports
- `reports.py` — `gen{Scene,Location,Character,Script}Report`: option
  dialog, build, show PDF (`trelby/reports.py:12-98`).
- `scriptreport.py` — `ScriptReport`: line counts per type, interior /
  exterior share, scene and action lengths, speaking characters.
- `scenereport.py` — `SceneReport` / `SceneInfo`: one entry per scene
  (heading, lines, pages, speakers).
- `locationreport.py` — `LocationReport`: scenes merged by `Locations`.
- `characterreport.py` — `CharacterReport` / `CharInfo`: speeches, lines,
  words, pages and scenes per speaking character.
- `dialoguechart.py` — `genDialogueChart` + `DialogueChart`: per-page bars of
  who speaks, with sort options (`trelby/dialoguechart.py:14`).
- `pagelist.py` — `PageList`: page numbers formatted as `1-3, 7`
  (`trelby/pagelist.py:6`).

Dialogs
- `cfgdlg.py` — `CfgDlg`: settings dialog; global pages or script pages
  from `configpages/` (`trelby/cfgdlg.py:21`).
- `finddlg.py` — `FindDlg`: find and replace, optional element-type filter;
  replace is one undo step per hit (`trelby/finddlg.py:403`).
- `spellcheck.py` — word list `dict_en.dat` (`loadDict`,
  `trelby/spellcheck.py:15`), user dictionaries (`Dict`), `SpellChecker`
  (walks the script word by word), `lev` (edit distance for suggestions).
- `spellcheckdlg.py` — `SpellCheckDlg`: replace / skip / add to script or
  global dictionary / suggest.
- `spellcheckcfgdlg.py` — `SCDictDlg`: edit a dictionary's word list.
- `namesdlg.py` — `NamesDlg`: character name database from `names.txt`
  (`readNames`, `trelby/namesdlg.py:14`), filter by type, sex and text,
  insert into the script.
- `namearray.py` — `NameArray`: compact storage for ~205 000 names with
  type and sex (`trelby/namearray.py:5`).
- `charmapdlg.py` — `CharMapDlg`: grid of the Latin-1 characters, inserts
  the selected one (`trelby/charmapdlg.py:25`).
- `titlesdlg.py` — `TitlesDlg`: edit title pages, with `TitlesPreview`.
- `titlespreview.py` — `TitlesPreview`: draws a title page scaled to the
  widget (`trelby/titlespreview.py:6`).
- `headersdlg.py` — `HeadersDlg`: edit page headers, PDF preview.
- `locationsdlg.py` — `LocationsDlg`: group scene headings into locations.
- `autocompletiondlg.py` — `AutoCompletionDlg`: edit completion lists.
- `commandsdlg.py` — `CommandsDlg`: HTML list of commands and their keys,
  can be saved to a file.
- `watermarkdlg.py` — `WatermarkDlg`: one watermarked PDF per line of text
  (`trelby/watermarkdlg.py:11`).

Data and folders
- `dict_en.dat` — English word list for the spell checker, one word per
  line (175 365 lines).
- `names.txt` — name database: `N<type>` lines start a group, `M<name>` /
  `F<name>` lines add names (204 761 lines).
- `__init__.py` — empty.
- `configpages/` — the settings-dialog pages (its own `CLAUDE.md`; two of
  them break when the GUI language is not English).
- `resources/` — icons, toolbar SVGs, splash logo, quotes (its own
  `CLAUDE.md`).
- `locales/` — compiled gettext catalogs `en` and `it` (its own `CLAUDE.md`).

## Key facts / gotchas
- **`_` is a builtin installed by `translations.trelby_translations_load()`**
  (`trelby/translations.py:26`); no module imports it. A test file run on its
  own fails with `NameError: name '_' is not defined` unless something
  imported `tests/test_validate.py`'s translation load first (seen running
  `tests/test_cut.py tests/test_myimport.py` alone: 8 failures). The full
  suite passes because collection imports `test_validate.py`.
- **`_("...".format(x))` formats before translating**, so the translated
  string is never found for those messages (e.g. `trelby/trelbyctrl.py:134`,
  `trelby/config.py:1227`). Throughout the package.
- **`TRELBY_TESTING` env var** makes `config`, `misc`, `util` and `gutil`
  import a `Mock` instead of `wx` (`trelby/config.py:14-19`) and leaves
  `ConfigGlobal.commands` empty (`trelby/config.py:687-690`).
- **Text input is Latin-1 only when typed**: `util.isValidInputChar`
  accepts codes 32–255 (`trelby/util.py:206`), but paste, import and
  find/replace do not filter (`util.toInputStr` only removes form feeds and
  turns tabs into `|`, `trelby/util.py:220`). The `toUTF8` / `fromUTF8` /
  `cleanInput` helpers are identity functions left from the Python 2 code
  (`trelby/util.py:194-232`).
- **Non-Latin-1 text in Helvetica or Times** (title pages) raises
  `IndexError`: `FontMetrics.getTextWidth` indexes a 256-entry table with
  `ord(ch)` (`trelby/fontinfo.py:57-60`). Courier has no table, so script
  text is safe.
- **Character map → Insert, Name database → Insert and Edit → Insert
  non-breaking space are broken:** they call
  `MyCtrl.OnKeyChar(util.MyKeyEvent(...))` (`trelby/charmapdlg.py:27`,
  `trelby/namesdlg.py:207-208`, `trelby/trelbyctrl.py:901`), but
  `OnKeyChar` calls `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1275`),
  which `util.MyKeyEvent` does not have (`trelby/util.py:776-797`) →
  `AttributeError`.
- **`opts.py --conf` crashes:** `str(sys.argv[i + 1], "UTF-8", "ignore")`
  (`trelby/opts.py:28`) raises `TypeError` on a `str` in Python 3.
- **`globaldata.makeConfDir` has an invalid `except` clause**
  `except OSError(os.errno, os.strerror)` (`trelby/globaldata.py:93`);
  `misc.init` already creates `confPath` (`trelby/misc.py:72-73`), so it is
  only reached if that failed.
- **`util.loadLatin1EncodedFile` reads bytes:** it passes `"ISO-8859-1"` as
  the `binary` argument of `loadFile` (`trelby/util.py:1013`). On
  `MemoryError`, `loadFile` returns an unbound `ret`
  (`trelby/util.py:990-1007`).
- **`Titles.sort()` does nothing**: it rebinds a local
  (`trelby/titles.py:60-61`), and its compare function has a typo
  `(a.x < a.y)` for `(a.x < b.x)` (`trelby/titles.py:58`).
- **Test-mode hotkeys collapsed**: the three `opts.isTest` characters in
  `OnKeyChar` became U+FFFD in an encoding conversion, so only the first
  branch (load `sample.trelby`) is reachable (`trelby/trelbyctrl.py:1298-1303`).
- **Exit "save" saves only the current tab** (`trelby/trelbyframe.py:972-973`
  → `OnSave`); other modified tabs are discarded.
- The MRU list is saved under the **translated** key `_("Files")`
  (`trelby/globaldata.py:70`), so switching `$LANG` loses the recent-files
  list.
- `misc.progPath` is the repository root (parent of `trelby/`,
  `trelby/misc.py:54`), so resources are addressed as
  `trelby/resources/...` (`trelby/splash.py:39`).
- `trelby/manual.html`, `dict_en.dat.gz`, `names.txt.gz` and `trelby.1.gz`
  are build products of `../Makefile`, not in git; Help → Manual opens
  `trelby/manual.html` (`trelby/trelbyframe.py:952`), which does not exist
  in a plain checkout.
- Two invalid escape sequences in `titles.py`, `" \qc"` / `" \qr"`
  (`trelby/titles.py:158-160`): `SyntaxWarning` in every test run, output
  unchanged.
- Most source files are UTF-8 even where the header says `iso-8859-1`
  (e.g. `trelby/trelbyctrl.py:1`).

## Touchpoints
- Called by: `../trelby.py`; `../tests/` (through `tests/u.py`).
- Depends on: wxPython 4 (GUI), lxml (HTML/FDX export, XML imports),
  ReportLab (PDF), stdlib `gettext`, `zipfile`, `zlib`, `difflib`.
  Versions: `../docker/requirements.lock`.
