## 3. Toolbar tooltips start off-screen

- **Status:** Open — a fix is in, waiting for Rafael's check on his screen
  (fixes/0000b1/toolbar-tooltips, 2026-10-31)
- **Symptom:** Tooltips of the vertical toolbar open partly outside the screen.
- **Where:** the toolbar is created with `wx.TB_VERTICAL`
  (`trelby/trelbyframe.py:244`); its tooltips were GTK's, from `shortHelp`.
- **Reproduce:** hover a toolbar icon (seen in Rafael's review of unmodified Trelby, 2026-10-23; `initiatives/README.md`).
- **Impact:** cosmetic.
- **Cause found (2026-10-31, in the real window on WSLg):** the displays are
  a 4K monitor at x 1920 and a full-HD one at (0, 563); X reports the
  window at (26, 23), on neither, and GTK places a tooltip by screen
  position, moved onto a monitor.
- **Fix tried:** no GTK tooltips on the toolbar; `OnToolEnter` shows the
  tip in a panel inside the window, right of the tool, level with the
  mouse (`trelby/trelbyframe.py:651`), so no screen position is used.
  Checked in the real window with a simulated hover (label, place, hidden
  on leave); still to check: hovering by hand. Once Rafael confirms, the
  status becomes Fixed.
