# config.py — as built

`trelby/config.py` (1574 lines) defines every setting Trelby has, split into
three objects, plus the tables that map line types and line breaks to their
one-character file codes. All saved settings go through `mypickle.Vars`
(`trelby/mypickle.py:8`).

## The three config objects

| object | scope | saved in | holds |
|---|---|---|---|
| `Config` (`trelby/config.py:378`) | one script | the script's `#Begin-Config` section | element layout and styles, paper, margins, font size, PDF options, `(MORE)`/`CONTINUED` strings, saved cursor |
| `ConfigGlobal` (`trelby/config.py:614`) | the program | `<confPath>/default.conf` | Enter/Tab table, keyboard commands, screen fonts and line height, colors, editor behaviour, PDF viewer, splash time |
| `ConfigGui` (`trelby/config.py:1433`) | the program, not saved | — | wx `Colour`/`Pen`/`Brush`/`Font` objects built from `ConfigGlobal` (wx objects cannot be deep-copied) |

## Classes

- `TypeInfo(lt, char, name)` (`trelby/config.py:88`) — fixed facts about a
  line type. Built once by `_init()` (`trelby/config.py:1615-1634`):

  | type | code | name |
  |---|---|---|
  | Scene | `\` | Scene |
  | Action | `.` | Action |
  | Character | `_` | Character |
  | Dialogue | `:` | Dialogue |
  | Parenthetical | `(` | Parenthetical |
  | Transition | `/` | Transition |
  | Shot | `=` | Shot |
  | Act break | `@` | Act break |
  | Note | `%` | Note |

  Line-break codes (`trelby/config.py:22-28`): `>` space, `+` space2, `&`
  none, `|` forced, `.` last.
- `TextType` (`trelby/config.py:102`) — `isCaps`, `isBold`, `isItalic`,
  `isUnderlined`.
- `Type(lt)` (`trelby/config.py:124`) — per script and type:
  `beforeSpacing` (0–50) and `intraSpacing` (0–20) in tenths of a line,
  `indent` (0–80) and `width` (5–80) in characters, and two `TextType`s,
  `screen` and `export` (`trelby/config.py:136-149`). Saved as
  `Element/<Name>/...`.
- `TypeGlobal(lt)` (`trelby/config.py:173`) — `newTypeEnter`, `newTypeTab`,
  `nextTypeTab`, `prevTypeTab` (`trelby/config.py:188-193`), saved by type
  name (`ElementNameVar`).
- `Command` (`trelby/config.py:211`) — `name`, `desc`, `defKeys`, `keys`
  (ints from `util.Key.toInt`), `isMovement`, `isFixed` (not saved, not
  rebindable), `isMenu`, `scrollDirection`. `load` drops bindings to plain
  input characters (`trelby/config.py:292-299`).
- `FontInfo` (`trelby/config.py:303`) — a `wx.Font` and its character
  width/height in pixels.
- `PDFFontInfo(name, style)` (`trelby/config.py:313`) — per script, one of
  `Normal`, `Bold`, `Italic`, `Bold-Italic`: PDF name and TTF file to embed;
  `refresh` strips characters not allowed in PostScript names
  (`trelby/config.py:368`).

## Defaults

- Per-script element layout (`Config.__init__`, `trelby/config.py:391-458`):

  | type | before | indent | width | screen | export |
  |---|---|---|---|---|---|
  | Scene | 10 | 0 | 60 | caps, bold | caps |
  | Action | 10 | 0 | 60 | — | — |
  | Character | 10 | 22 | 38 | caps | caps |
  | Dialogue | 0 | 10 | 35 | — | — |
  | Parenthetical | 0 | 16 | 25 | — | — |
  | Transition | 10 | 45 | 20 | caps | caps |
  | Shot | 10 | 0 | 60 | caps | caps |
  | Act break | 10 | 25 | 10 | caps, bold, underlined | caps, underlined |
  | Note | 10 | 5 | 55 | italic | italic |

- Per-script page (`Config.setupVars`, `trelby/config.py:473-539`): A4
  210 × 297 mm, margins top 12.7 / bottom 25.4 / left 38.1 / right 25.4 mm,
  font size 12 pt, keep ≥ 2 action and ≥ 2 dialogue lines at a page
  bottom, scene continueds off, scene numbers off, PDF TOC on, open PDF on
  current page on, notes outlined, strings `(MORE)`, `(CONTINUED)`,
  `CONTINUED:`, ` (cont'd)`.
- Global (`ConfigGlobal.setupVars`, `trelby/config.py:1153-1261`): splash
  3 s, draft line height `fontYdelta` 18 px, screen zoom 100 % (`zoom`,
  50–300, `trelby/config.py:1164`), mouse wheel 4 lines,
  re-paginate every 1 s, check errors before export, capitalize sentences
  and `i`, open scripts at the saved position, overwrite selection on
  typing, page-break indicators "real" only.
- Enter/Tab table: `trelby/config.py:627-689` (also printed in
  `../trelby.process.md`, stage 3).
- Screen fonts: empty in `setupVars`, filled by `setDefaultFonts`
  (`trelby/config.py:1400`): `Monospace 12` (+ Bold / Italic / Bold Italic)
  on Unix, Courier New with LOGFONT height `-13` on Windows. They are
  stored unzoomed; the zoom is applied in `ConfigGui`.

## Key functions

- `Config.load(s)` / `save()` (`trelby/config.py:543-566`),
  `Config.recalc(doAll)` (`trelby/config.py:577`): clamps every numeric
  value to its range, cleans strings, zeroes top/bottom margins if less than
  100 mm of paper would be left, and computes `linesOnPage`
  (`trelby/config.py:596-599`).
- `ConfigGlobal.load` / `save` (`trelby/config.py:1265-1288`), `recalc`
  (clamp only, `trelby/config.py:1291`), `addShiftKeys` (Shift+key aliases
  for movement commands, so Shift selects, `trelby/config.py:1324`),
  `removeKey`, `getConflictingKeys` (`trelby/config.py:1353`),
  `setDefaults` (`trelby/config.py:1381`), `findPDFViewer`
  (`trelby/config.py:1424`).
- Zoom (`trelby/config.py:1295-1317`): `setZoom(z)` snaps to `ZOOM_STEP`
  (10) and clamps to `ZOOM_MIN`–`ZOOM_MAX` (50–300, `trelby/config.py:74-77`),
  returning whether it changed; `zoomIn` / `zoomOut` / `zoomReset` step
  from it; `zoomScale(val)` scales a screen size by `zoom / 100`. The
  commands `ZoomIn` (Ctrl `+`, Ctrl Shift `+`, Ctrl `=`), `ZoomOut`
  (Ctrl `-`) and `ZoomReset` (Ctrl `0`) are menu-type commands, so they run
  `MyFrame.On<Name>` (`trelby/config.py:1126-1147`).
- `ConfigGui.__init__(cfgGl)` (`trelby/config.py:1441`): one
  `<name>Color` attribute per color setting, pens and brushes, and the four
  screen fonts, each `Scaled` by `zoom / 100` (`trelby/config.py:1546-1548`),
  and `fontYdelta`, the draft row height at the current zoom
  (`trelby/config.py:1558`); `tt2fi(textType)` picks the font by bold/italic
  (`trelby/config.py:1561`); `lt2textColor(lt)` (`trelby/config.py:1565`).
- Module functions (`trelby/config.py:1569-1611`): `getTIs`, `char2lb`,
  `lb2char`, `lb2str`, `char2lt`, `lt2char`, `name2ti`, `lt2ti`.

## Extension points

- **Element types** — `_init()` table, `Config.__init__` defaults,
  `ConfigGlobal.__init__` Enter/Tab row, `ChangeTo<Type>` command; the full
  list of places is in `screenplay.as-built.md` (Extension points).
- **Tab order** — the four `TypeGlobal` fields per type
  (`trelby/config.py:627-689`); editable in Settings → Elements
  (`trelby/configpages/elementsglobalpanel.py:6`). Global, not per script.
- **Colors** — `v.addColor(name, r, g, b, saveName, description)` in
  `ConfigGlobal.setupVars` (`trelby/config.py:1212-1259`). `addColor`
  appends `Color` to the attribute name (`trelby/mypickle.py:93-96`), so
  `text` → `cfgGl.textColor` and `cfgGui.textColor`. The settings page lists
  every color var automatically (`trelby/configpages/colorspanel.py:8`).
  Per-element text colors `text<Name>Color` exist for each type but are used
  only when `useCustomElemColors` is on (`trelby/trelbyctrl.py:1525-1528`).
  There is no theme concept: one set of values, light by default.
- **Screen fonts / zoom** — `fontNormal` … `fontBoldItalic`
  (`trelby/config.py:1203-1206`) are `wx.NativeFontInfo` strings; draft
  line spacing is `fontYdelta` (`trelby/config.py:1160`). Layout modes scale
  page millimeters to pixels from the normal font's character width
  (`trelby/viewmode.py:404-407`), so scaling the fonts is the zoom: the
  `zoom` setting scales the `wx.Font`s and `fontYdelta` in `ConfigGui`
  only, never `cfgGl`'s strings or the script's PDF `fontSize`.
- **New setting** — add a `v.add*` line in the right `setupVars`; load,
  save, defaults and clamping follow from `mypickle`. A setting used only
  internally gets an empty save name (`trelby/mypickle.py:121-127`).

## Gotchas

- **`ConfigGlobal.commands` must be in alphabetical order**:
  `setDefaults` raises `ConfigError` otherwise (`trelby/config.py:1383-1394`).
- Under `TRELBY_TESTING` `wx` is a `Mock` and `commands` is empty
  (`trelby/config.py:14-19`, `trelby/config.py:692-695`).
- The color for Act break is the attribute `textAct breakColor` (with a
  space) and the save key `Color/TextAct breakFG`, built from the type name
  (`trelby/config.py:1251-1259`, `trelby/config.py:1460`).
- `Config.load` and `ConfigGlobal.load` never raise: unknown keys are
  ignored, bad values fall back to defaults and are clamped
  (`trelby/config.py:541-554`). Old keys such as
  `Element/Scene/AutoCompletion` in `tests/fixtures/test.trelby` are
  silently dropped.
- `ConfigGlobal` setting `scriptDir` defaults to `misc.progPath`
  (`trelby/config.py:1209`), so `misc.init()` must have run before
  `ConfigGlobal.setupVars` (first instantiation).
- `_("Text foreground for {}".format(t.name))` is formatted before
  translation, so it is never translated (`trelby/config.py:1258`). Bug: [bugs/config-i18n/3](../initiatives/bugs/epics/config-i18n/tasks/3-format-before-translate.md).

## Tests

- No dedicated test. `ConfigGlobal()` and `Config` are built by every test
  through `tests/u.py`; `tests/test_ismodified.py` calls `applyCfg`;
  `tests/test_renderscreenplay.py` sets `PDFFontInfo` fields. Load/save of
  `default.conf`, `ConfigGui` and key bindings are not covered.
