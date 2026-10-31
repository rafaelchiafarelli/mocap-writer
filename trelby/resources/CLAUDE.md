# resources — images and texts loaded at run time

**Role:** Icons, toolbar images, the splash logo and quotes. Files are addressed as `trelby/resources/<file>` relative to
`misc.progPath` (the repository root, `trelby/misc.py:54`).
**Entry points:** none; read by `MyFrame.addTB` (toolbar SVGs,
`trelby/trelbyframe.py:250-292`), `MyFrame.mySetIcons` (window icons,
`trelby/trelbyframe.py:502-510`), `SplashWindow` (`trelby/splash.py:39`,
`trelby/splash.py:124`), `MyFSButton` (`trelby/misc.py:131`).
**Inputs → Outputs:** static files → bitmaps and text in the GUI.

## Files
- Toolbar icons (SVG, 32 × 32, black fills recolored to `#CCCCCC` when the
  system theme is dark, `trelby/trelbyframe.py:257-258`): `new.svg`,
  `open.svg`, `save.svg`, `saveas.svg`, `close.svg`, `scrset.svg`
  (script settings), `pdf.svg` (print), `import.svg`, `export.svg`,
  `undo.svg`, `redo.svg`, `find.svg`, `sync.svg` (Sync to spec, two
  arrows in a circle, made for mocap-writer 2026-10-31), `view.svg`,
  `report.svg`, `tools.svg`, `settings.svg`.
- Window icons: `icon16.png`, `icon32.png`, `icon64.png`, `icon128.png`,
  `icon256.png`.
- `fullscreen.png` — the "exit fullscreen" button.
- `logo.jpg` — splash and About image (the text drawn on it is placed for
  its size, `trelby/splash.py:84-86`).
- `quotes.txt` — splash quotes: one to three lines, then the source on a
  line indented by two spaces; `#` comments; UTF-8
  (`trelby/splash.py:121-164`).
- `README` — the non-custom icons come from the Faenza icon set, GPL.

## Key facts / gotchas
- Every file here but `README` is read by the code; the unused PNG
  toolbar icons, stray SVGs, `icon256.ico` and `trelby.desktop` were
  removed with the packaging (2026-10-31).
- Licenses: Faenza icons are GPL (allowed for tools under the Mocap Studio
  license rule); the other files have no license note of their own and fall
  under the repository's GPL-2.0 (`LICENSE`). `quotes.txt` holds
  short quotes from films.

## Touchpoints
- Called by: `trelby/trelbyframe.py`, `trelby/splash.py`, `trelby/misc.py`.
