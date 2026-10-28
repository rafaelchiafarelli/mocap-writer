# config.py — as built

`trelby/config.py` (1574 lines) defines every setting Trelby has, split into
three objects, plus the tables that map line types and line breaks to their
one-character file codes. All saved settings go through `mypickle.Vars`
(`trelby/mypickle.py:8`).

## The three config objects

| object | scope | saved in | holds |
|---|---|---|---|
| `Config` (`trelby/config.py:433`) | one script | the script's `#Begin-Config` section | element layout and styles, paper, margins, font size, PDF options, `(MORE)`/`CONTINUED` strings, saved cursor |
| `ConfigGlobal` (`trelby/config.py:669`) | the program | `<confPath>/default.conf` | Enter/Tab table, Tab cycle, keyboard commands, screen fonts and line height, colors, editor behaviour, PDF viewer, splash time |
| `ConfigGui` (`trelby/config.py:1590`) | the program, not saved | — | wx `Colour`/`Pen`/`Brush`/`Font` objects built from `ConfigGlobal` (wx objects cannot be deep-copied) |

## Classes

- `TypeInfo(lt, char, name)` (`trelby/config.py:144`) — fixed facts about a
  line type. Built once by `_init()` (`trelby/config.py:1776-1795`):

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
- `TextType` (`trelby/config.py:158`) — `isCaps`, `isBold`, `isItalic`,
  `isUnderlined`.
- `Type(lt)` (`trelby/config.py:180`) — per script and type:
  `beforeSpacing` (0–50) and `intraSpacing` (0–20) in tenths of a line,
  `indent` (0–80) and `width` (5–80) in characters, and two `TextType`s,
  `screen` and `export` (`trelby/config.py:192-205`). Saved as
  `Element/<Name>/...`.
- `TypeGlobal(lt)` (`trelby/config.py:229`) — `newTypeEnter`, `newTypeTab`
  (`trelby/config.py:244-245`), saved by type name (`ElementNameVar`). What
  Tab / Shift+Tab convert to is not per type: it is
  `ConfigGlobal.tabOrder` (see Tab cycle below). Old configs still carry
  `Element/<Name>/NextTypeTab` / `PrevTypeTab`; they are ignored.
- `Command` (`trelby/config.py:266`) — `name`, `desc`, `defKeys`, `keys`
  (ints from `util.Key.toInt`), `isMovement`, `isFixed` (not saved, not
  rebindable), `isMenu`, `scrollDirection`. `load` drops bindings to plain
  input characters (`trelby/config.py:347-354`).
- `FontInfo` (`trelby/config.py:358`) — a `wx.Font` and its character
  width/height in pixels.
- `PDFFontInfo(name, style)` (`trelby/config.py:368`) — per script, one of
  `Normal`, `Bold`, `Italic`, `Bold-Italic`: PDF name and TTF file to embed;
  `refresh` strips characters not allowed in PostScript names
  (`trelby/config.py:423`).

## Defaults

- Per-script element layout (`Config.__init__`, `trelby/config.py:446-513`):

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

- Per-script page (`Config.setupVars`, `trelby/config.py:528-594`): A4
  210 × 297 mm, margins top 12.7 / bottom 25.4 / left 38.1 / right 25.4 mm,
  font size 12 pt, keep ≥ 2 action and ≥ 2 dialogue lines at a page
  bottom, scene continueds off, scene numbers off, PDF TOC on, open PDF on
  current page on, notes outlined, strings `(MORE)`, `(CONTINUED)`,
  `CONTINUED:`, ` (cont'd)`.
- Global (`ConfigGlobal.setupVars`, `trelby/config.py:1202-1328`): splash
  3 s, draft line height `fontYdelta` 18 px, screen zoom 100 % (`zoom`,
  50–300, `trelby/config.py:1213`), mouse wheel 4 lines,
  re-paginate every 1 s, check errors before export, capitalize sentences
  and `i`, open scripts at the saved position, overwrite selection on
  typing, page-break indicators "real" only, theme Light (`theme`,
  `trelby/config.py:1226`).
- Tab cycle `tabOrder` (`trelby/config.py:1215-1223`): Scene → Action →
  Character → Dialogue (`TAB_ORDER_DEFAULT`, `trelby/config.py:94`), saved
  as `TabOrder` (a count, then `TabOrder/<n>:<element name>`).
- Enter/Tab table: `trelby/config.py:694-738` (also printed in
  `../trelby.process.md`, stage 3).
- Screen fonts: empty in `setupVars`, filled by `setDefaultFonts`
  (`trelby/config.py:1557`): `Monospace 12` (+ Bold / Italic / Bold Italic)
  on Unix, Courier New with LOGFONT height `-13` on Windows. They are
  stored unzoomed; the zoom is applied in `ConfigGui`.

## Key functions

- `Config.load(s)` / `save()` (`trelby/config.py:598-621`),
  `Config.recalc(doAll)` (`trelby/config.py:632`): clamps every numeric
  value to its range, cleans strings, zeroes top/bottom margins if less than
  100 mm of paper would be left, and computes `linesOnPage`
  (`trelby/config.py:651-654`).
- `ConfigGlobal.load` / `save` (`trelby/config.py:1332-1385`): colors are
  loaded and saved per theme from `themeColors` (see Themes below); every
  other setting through `cvars`. `recalc`
  (clamps numbers and cleans `tabOrder`: repeats dropped, fewer than two
  entries → the default, `trelby/config.py:1419-1429`), `addShiftKeys` (Shift+key aliases
  for movement commands, so Shift selects, `trelby/config.py:1481`),
  `removeKey`, `getConflictingKeys` (`trelby/config.py:1510`),
  `setDefaults` (`trelby/config.py:1538`), `findPDFViewer`
  (`trelby/config.py:1581`).
- Zoom (`trelby/config.py:1452-1474`): `setZoom(z)` snaps to `ZOOM_STEP`
  (10) and clamps to `ZOOM_MIN`–`ZOOM_MAX` (50–300, `trelby/config.py:74-77`),
  returning whether it changed; `zoomIn` / `zoomOut` / `zoomReset` step
  from it; `zoomScale(val)` scales a screen size by `zoom / 100`. The
  commands `ZoomIn` (Ctrl `+`, Ctrl Shift `+`, Ctrl `=`), `ZoomOut`
  (Ctrl `-`) and `ZoomReset` (Ctrl `0`) are menu-type commands, so they run
  `MyFrame.On<Name>` (`trelby/config.py:1175-1196`).
- Tab cycle (`trelby/config.py:1434-1450`): `nextTypeTab(lt)` /
  `prevTypeTab(lt)` step `tabOrder` forward / backward, wrapping around; an
  element outside the cycle enters it at Action (or at the first entry if
  Action is not in it).
- Themes (`trelby/config.py:1388-1417`): `getThemeDefault(theme, name)`
  (light: the `addColor` value; dark: `DARK_COLORS`), `storeThemeColors` /
  `loadThemeColors` copy the color attributes to / from the active theme's
  entry of `themeColors`, `setTheme(t)` stores, switches and loads,
  returning whether it changed.
- `ConfigGui.__init__(cfgGl)` (`trelby/config.py:1598`): one
  `<name>Color` attribute per color setting, pens and brushes (among them
  `sceneHatchBrush`, a `BDIAGONAL_HATCH` of the `sceneHatch` color, light
  160,176,210, dark 78,88,110, `trelby/config.py:1299`), and the four
  screen fonts, each `Scaled` by `zoom / 100` (`trelby/config.py:1707-1709`),
  and `fontYdelta`, the draft row height at the current zoom
  (`trelby/config.py:1719`); `tt2fi(textType)` picks the font by bold/italic
  (`trelby/config.py:1722`); `lt2textColor(lt)` (`trelby/config.py:1726`).
- Module functions (`trelby/config.py:1730-1772`): `getTIs`, `char2lb`,
  `lb2char`, `lb2str`, `char2lt`, `lt2char`, `name2ti`, `lt2ti`.

## Extension points

- **Element types** — `_init()` table, `Config.__init__` defaults,
  `ConfigGlobal.__init__` Enter/Tab row, `ChangeTo<Type>` command; the full
  list of places is in `screenplay.as-built.md` (Extension points).
- **Tab order** — `newTypeEnter` / `newTypeTab` per type
  (`trelby/config.py:694-738`, editable in Settings → Elements,
  `trelby/configpages/elementsglobalpanel.py:6`) and the one `tabOrder`
  cycle (config file only, no settings page). Global, not per script.
- **Colors** — `v.addColor(name, r, g, b, saveName, description)` in
  `ConfigGlobal.setupVars` (`trelby/config.py:1274-1326`). `addColor`
  appends `Color` to the attribute name (`trelby/mypickle.py:93-96`), so
  `text` → `cfgGl.textColor` and `cfgGui.textColor`. The settings page lists
  every color var automatically (`trelby/configpages/colorspanel.py:8`).
  Per-element text colors `text<Name>Color` exist for each type but are used
  only when `useCustomElemColors` is on (`trelby/trelbyctrl.py:1797-1800`).
  A new color also needs its dark value in `DARK_COLORS`
  (`tests/test_theme.py` fails otherwise).
- **Themes** — `theme` (`THEME_LIGHT` 0 / `THEME_DARK` 1,
  `trelby/config.py:79-91`) chooses which set the color attributes hold.
  `ConfigGlobal.themeColors` (`trelby/config.py:683`) keeps every theme's
  colors, `{theme: {attribute: MyColor}}`; the active theme's colors are
  the attributes themselves (what `ConfigGui` and the colors page use),
  its `themeColors` entry is refreshed on save and on switch. The dark
  defaults are declared once, in `DARK_COLORS` (`trelby/config.py:105`).
  Saved: light colors under the original `Color/<Name>` keys, dark under
  `Dark/Color/<Name>` (`THEME_SAVE_PREFIX`), so a config from before themes
  loads as light with the dark defaults. Screen only: the PDF has its own
  colors. GTK's dark variant (menus, toolbar, dialogs) is picked by
  `docker/run.sh` from `Theme:1` at start, so it changes on restart; the
  script view changes at once.
- **Screen fonts / zoom** — `fontNormal` … `fontBoldItalic`
  (`trelby/config.py:1265-1268`) are `wx.NativeFontInfo` strings; draft
  line spacing is `fontYdelta` (`trelby/config.py:1209`). Layout modes scale
  page millimeters to pixels from the normal font's character width
  (`trelby/viewmode.py:430-433`), so scaling the fonts is the zoom: the
  `zoom` setting scales the `wx.Font`s and `fontYdelta` in `ConfigGui`
  only, never `cfgGl`'s strings or the script's PDF `fontSize`.
- **New setting** — add a `v.add*` line in the right `setupVars`; load,
  save, defaults and clamping follow from `mypickle`. A setting used only
  internally gets an empty save name (`trelby/mypickle.py:121-127`).

## Gotchas

- **`ConfigGlobal.commands` must be in alphabetical order**:
  `setDefaults` raises `ConfigError` otherwise (`trelby/config.py:1540-1551`).
- Under `TRELBY_TESTING` `wx` is a `Mock` and `commands` is empty
  (`trelby/config.py:14-19`, `trelby/config.py:741-744`).
- The color for Act break is the attribute `textAct breakColor` (with a
  space) and the save key `Color/TextAct breakFG`, built from the type name
  (`trelby/config.py:1318-1326`, `trelby/config.py:1617`).
- `Config.load` and `ConfigGlobal.load` never raise: unknown keys are
  ignored, bad values fall back to defaults and are clamped
  (`trelby/config.py:596-609`).
- `ConfigGlobal` setting `scriptDir` defaults to `misc.progPath`
  (`trelby/config.py:1271`), so `misc.init()` must have run before
  `ConfigGlobal.setupVars` (first instantiation).

## Tests

- No dedicated test. `ConfigGlobal()` and `Config` are built by every test
  through `tests/u.py`; `tests/test_ismodified.py` calls `applyCfg`;
  `tests/test_renderscreenplay.py` sets `PDFFontInfo` fields. Load/save of
  `default.conf`, `ConfigGui` and key bindings are not covered.
