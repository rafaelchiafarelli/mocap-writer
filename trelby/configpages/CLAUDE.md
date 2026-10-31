# configpages — the pages of the settings dialogs

**Role:** One `wx.Panel` per page of `CfgDlg` (`trelby/cfgdlg.py:21`). Each
page edits a deep copy of a config object in place; the dialog's Apply / OK
hands that copy to `MyCtrl.applyGlobalCfg` or `MyCtrl.applyCfg`
(`trelby/trelbyctrl.py:607-653`).
**Entry points:** `CfgDlg.AddPage(PanelClass, name)` (`trelby/cfgdlg.py:80`)
instantiates `PanelClass(listbook, -1, cfg)` or, for the four pages that
open their own dialogs, `PanelClass(listbook, -1, cfg, cfgDlg)`
(`trelby/cfgdlg.py:82-86`).
**Inputs → Outputs:** a `config.ConfigGlobal` (File → Settings) or a
`config.Config` (Script → Settings) → the same object, modified. Every page
follows the pattern: build widgets, `cfg2gui()` to fill them, `OnMisc()` to
write them back on every change.

## Files

Global settings (`ConfigGlobal`)
- `globalaboutpanel.py` — `GlobalAboutPanel`: explanatory text only.
- `colorspanel.py` — `ColorsPanel`: a Light / Dark theme choice
  (`cfg.setTheme`, `trelby/configpages/colorspanel.py:16-37`), the list of
  every color var in `cfg.cvars.color` (the chosen theme's values), change /
  reset to the theme's default (`cfg.getThemeDefault`), and the
  `useCustomElemColors` switch (`trelby/configpages/colorspanel.py:8`).
- `displaypanel.py` — `DisplayPanel`: the four screen fonts (rejects
  non-fixed-width fonts; picking one also sets `fontYdelta` to the font's
  height, `trelby/configpages/displaypanel.py:95-121`), row spacing
  `fontYdelta`, page-break indicators.
- `elementsglobalpanel.py` — `ElementsGlobalPanel`: the Enter/Tab table,
  two combos per element type, Enter creates / Tab creates
  (`trelby/configpages/elementsglobalpanel.py:35-36`). The Tab / Shift+Tab
  cycle (`ConfigGlobal.tabOrder`) has no settings page.
- `keyboardpanel.py` — `KeyboardPanel`: per command, list / add / delete
  keys, show conflicts (`trelby/configpages/keyboardpanel.py:6`).
- `miscpanel.py` — `MiscPanel`: default script directory, PDF viewer path and
  arguments (with Guess), editor switches, the spell checker language
  (`spellLanguage`, spellcheck/pt-br/1), splash time, auto-paginate
  interval, mouse-wheel lines (`trelby/configpages/miscpanel.py:8`).

Script settings (`Config`)
- `scriptaboutpanel.py` — `ScriptAboutPanel`: explanatory text only.
- `elementspanel.py` — `ElementsPanel`: per element type, spacing before /
  between, indent, width, screen and export styles
  (`trelby/configpages/elementspanel.py:8`).
- `formattingpanel.py` — `FormattingPanel`: lines of action/dialogue kept
  at a page bottom, font size, scene CONTINUEDs and their indent, scene
  numbers, line numbers.
- `paperpanel.py` — `PaperPanel`: A4 / Letter / Custom size, margins in mm
  or inches, lines per page (`trelby/configpages/paperpanel.py:13-15`).
- `pdfpanel.py` — `PDFPanel`: TOC, open on current page, omit or outline
  notes, show margins.
- `pdffontspanel.py` — `PDFFontsPanel`: per style a PDF font name and a
  TTF file; reads the file's PostScript name and embedding flag with
  `truetype.Font` (`trelby/configpages/pdffontspanel.py:146-184`).
- `stringspanel.py` — `StringsPanel`: `(MORE)`, `(CONTINUED)`,
  `CONTINUED:`, `(cont'd)` texts.

Shared
- `aboutpanel.py` — `AboutPanel`: a panel showing one text, base of the two
  About pages.

## Key facts / gotchas
- Widgets are found by attribute names built in helpers
  (`addCheckBox`, `addMarginCtrl`, `addEntry`, `addTypeCombo`): those
  names come from a fixed key, never from the translated label, or a page
  breaks outside English (fixed 2026-10-27, bugs/config-i18n/2;
  `tests/test_i18n.py`).
- The folder has no `__init__.py`; `trelby.configpages.*` imports work as a
  namespace package (`trelby/cfgdlg.py:4-18`).
- Pages hold no state of their own beyond widgets; cancelling the dialog
  just drops the deep copy (`trelby/trelbyctrl.py:1523-1541`).

## Touchpoints
- Called by: `trelby/cfgdlg.py`.
- Depends on: `trelby/config.py` (the objects edited), `trelby/util.py`,
  `trelby/misc.py`, `trelby/gutil.py`, `trelby/truetype.py`.
