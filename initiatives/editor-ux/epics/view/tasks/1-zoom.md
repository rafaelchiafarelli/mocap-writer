## 1. Zoom

- **Status:** Done (2026-10-24) — `ConfigGlobal.zoom` + `ConfigGui`
  scaling, commands, Ctrl + wheel, status control; `tests/test_zoom.py`;
  checked on screen (WSLg) in draft and layout. Open question for Rafael:
  no horizontal scrolling, so a page wider than the window is cut on the
  right at high zoom
- **Type:** code
- **Depends on:** —
- **Contract:**
  - In: Ctrl + `+` / Ctrl + `-` / Ctrl + `0`, Ctrl + mouse wheel, and a zoom
    control in the status bar
  - Requires: scales only the script view (the screen fonts in `ConfigGlobal`
    and everything measured from them); toolbar, menus and dialogs stay the
    same size; the PDF output is not affected; the zoom level is kept in the
    global settings
  - Delivers: zoom from 50 % to 300 % in steps of 10 %
- **Pre-work:** —
- **Out of scope:** per-script zoom
- **Tests:** zoom changes the view's font size and not `fontSize` (PDF); the
  level survives a restart (settings round trip)
