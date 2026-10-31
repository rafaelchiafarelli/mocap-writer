# locales — compiled translation catalog

**Role:** The gettext catalog the program needs at startup:
`en/LC_MESSAGES/trelby.mo`.
**Entry points:** `translations.trelby_translations_load()`
(`trelby/translations.py:10`) loads `trelby.mo` for `$LANG`, its base
language (`pt_BR.UTF-8` → `pt`), or `en`, and installs `_`.
**Inputs → Outputs:** this file → the GUI strings (English).

## Files
- `en/LC_MESSAGES/trelby.mo` — English (identity) catalog.

## Key facts / gotchas
- English is the only GUI language Mocap Studio needs (Rafael,
  2026-10-27). The Italian catalog, the `po/` sources and the `t_0*.sh`
  build scripts were removed (2026-10-31), so the `.mo` is never rebuilt.
  A message missing from it is shown as written in the code, which is the
  same English, so new strings need no catalog update.
- `gettext.translation(...)` is called without `fallback=True`
  (`trelby/translations.py:25`): without `en`, startup would fail, so this
  file stays.

## Touchpoints
- Called by: `trelby/translations.py`.
