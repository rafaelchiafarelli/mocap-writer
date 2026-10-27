# po — translation sources (gettext)

**Role:** The editable translation files. Compiled into
`trelby/locales/<lang>/LC_MESSAGES/trelby.mo`.
**Entry points:** the three root scripts, run from the repository root
(`TRANSLATION_NOTES.txt`):
`t_01_update_pot.sh` (xgettext over `trelby/**/*.py` → `trelby.pot`),
`t_02_update_po.sh` (msgmerge into each `.po`),
`t_03_build.sh` (msgfmt → `trelby/locales/`).
**Inputs → Outputs:** `_("…")` strings in the code → `trelby.pot` →
`<lang>.po` (translated by hand) → `.mo`.

## Files
- `trelby.pot` — template of all translatable strings, generated
  2025-10-03 for 2.4.16.
- `en.po` — English (identity) catalog.
- `it.po` — Italian catalog.

## Key facts / gotchas
- `t_01_update_pot.sh` uses `xgettext -j` (join), so strings removed from
  the code stay in the template until cleaned by hand.
- Messages with `{}` placeholders are looked up before formatting
  (`_("…{}").format(x)`), so a translation must keep the same placeholders;
  `it.po` and `en.po` do (checked 2026-10-27).
- Needs the gettext tools, which are not in the Docker image.

## Touchpoints
- Built into: `trelby/locales/`.
- Generated from: every `trelby/*.py` and `trelby/configpages/*.py`.
