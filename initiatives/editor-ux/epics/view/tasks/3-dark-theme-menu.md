## 3. Dark theme in the View menu

- **Status:** Done (2026-10-24) — `ID_VIEW_DARK_THEME` check item
  "Dark theme" after "Show formatting"; `MyFrame.OnDarkTheme` →
  `MyCtrl.OnDarkTheme` (setTheme, rebuild `ConfigGui`, repaint, save
  config); `MyFrame.updateThemeMenu` from `applyGlobalCfg` keeps it in step
  with Settings → Colors. Checked in the running editor: check → Dark and
  `Theme:1` saved, uncheck → Light, Settings → Dark checks the item
  (review copy `mocap-writer-view-menu-dark-theme.png`)

- **Type:** code
- **Depends on:** view/2 (the themes)
- **Contract:**
  - In: View → Dark theme, a check item (Rafael, 2026-10-24)
  - Requires: checking it switches to the Dark theme, unchecking to Light,
    at once and without losing custom colors (`ConfigGlobal.setTheme`); the
    choice is saved to the global config like the zoom; the check follows
    the theme chosen in Settings → Colors
  - Delivers: the menu item and its handler
- **Pre-work:** —
- **Out of scope:** menus and dialogs switching to GTK's dark variant
  without a restart (GTK reads `GTK_THEME` at start, `docker/run.sh`)
- **Tests:** `setTheme` is already covered by `tests/test_theme.py`; the
  menu needs a display, so it is checked on a render of the editor
