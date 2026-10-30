# resources — images and texts loaded at run time

**Role:** Icons, toolbar images, the splash logo and quotes, and the Linux
desktop entry. Files are addressed as `trelby/resources/<file>` relative to
`misc.progPath` (the repository root, `trelby/misc.py:54`).
**Entry points:** none; read by `MyFrame.addTB` (toolbar SVGs,
`trelby/trelbyframe.py:216-261`), `MyFrame.mySetIcons` (window icons,
`trelby/trelbyframe.py:449-457`), `SplashWindow` (`trelby/splash.py:39`,
`trelby/splash.py:124`), `MyFSButton` (`trelby/misc.py:131`).
**Inputs → Outputs:** static files → bitmaps and text in the GUI.

## Files
- Toolbar icons (SVG, 32 × 32, black fills recolored to `#CCCCCC` when the
  system theme is dark, `trelby/trelbyframe.py:223-224`): `new.svg`,
  `open.svg`, `save.svg`, `saveas.svg`, `close.svg`, `scrset.svg`
  (script settings), `pdf.svg` (print), `import.svg`, `export.svg`,
  `undo.svg`, `redo.svg`, `find.svg`, `view.svg`, `report.svg`,
  `tools.svg`, `settings.svg`.
- Window icons: `icon16.png`, `icon32.png`, `icon64.png`, `icon128.png`,
  `icon256.png`; `icon256.ico` is used only by the Chocolatey shortcut
  (`choco/tools/chocolateyinstall.ps1:2`).
- `fullscreen.png` — the "exit fullscreen" button.
- `logo.jpg` — splash and About image (the text drawn on it is placed for
  its size, `trelby/splash.py:84-86`).
- `quotes.txt` — splash quotes: one to three lines, then the source on a
  line indented by two spaces; `#` comments; UTF-8
  (`trelby/splash.py:121-164`).
- `trelby.desktop` — Linux desktop entry, installed by `debian/install`.
- Not referenced by any code or packaging file: `close.png`, `pdf.png`,
  `scrset.png`, `settings.png` (PNG versions from before the SVG toolbar),
  `drawing.svg`, `layout.svg`, `trelby.svg`.
- `README` — the non-custom icons come from the Faenza icon set, GPL.

## Key facts / gotchas
- `trelby.desktop` says `Icon=trelby256`, but `debian/install` copies
  `icon256.png` to `/usr/share/resources` (`debian/install:1`), not to an
  icon theme directory, so the desktop entry's icon is not found by name. (bugs/tooling/6, left as upstream's: `debian/CLAUDE.md`).
- Licenses: Faenza icons are GPL (allowed for tools under the Mocap Studio
  license rule); the other files have no license note of their own and fall
  under the repository's GPL-3.0-or-later (`setup.cfg`). `quotes.txt` holds
  short quotes from films.

## Touchpoints
- Called by: `trelby/trelbyframe.py`, `trelby/splash.py`, `trelby/misc.py`.
- Packaged by: `setup.cfg` (`resources/*`), `debian/install`,
  `tools/update_icns.py` (rebuilds `resources_mac/icon.icns`).
