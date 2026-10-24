## 2. Dark theme

- **Status:** Done (2026-10-24) — `ConfigGlobal.theme` + `themeColors`
  (each theme keeps its own colors), `DARK_COLORS` declared once, Light /
  Dark choice in Settings → Colors, `GTK_THEME=Adwaita:dark` from
  `docker/run.sh`; `tests/test_theme.py`. Smoke-run in Dark (no errors);
  not checked by eye on screen
- **Type:** code
- **Depends on:** —
- **Contract:**
  - In: a Light / Dark choice in the settings
  - Requires: a theme is a named set of the existing `ConfigGlobal` colors
    (text, page, workspace, notes, cursor, tabs…); the dark set is declared in
    one place, not scattered; menus, toolbar and dialogs follow GTK's dark
    variant (`GTK_THEME=Adwaita:dark` in `docker/run.sh` when Dark is chosen)
  - Delivers: the two themes, switchable without losing custom colors
- **Pre-work:** —
- **Out of scope:** a theme editor; PDF colors (always print colors)
- **Tests:** every color in the dark set is defined; switching keeps the
  user's custom colors; text/background contrast ≥ 4.5:1 for each element
