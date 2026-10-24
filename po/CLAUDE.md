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
- Strings written as `_("…{}".format(x))` reach `xgettext` with the `{}`
  placeholder but are looked up after formatting, so they are never
  translated at run time (`trelby/CLAUDE.md`, gotchas). Bug: [bugs/config-i18n/3](../initiatives/bugs/epics/config-i18n/tasks/3-format-before-translate.md).
- `TRANSLATION_NOTES.txt` lists `t_01_update_pot.sh` twice; the second step
  is meant to be `t_02_update_po.sh`. Bug: [bugs/tooling/7](../initiatives/bugs/epics/tooling/tasks/7-translation-notes-step.md).
- Needs the gettext tools, which are not in the Docker image.

## Touchpoints
- Built into: `trelby/locales/`.
- Generated from: every `trelby/*.py` and `trelby/configpages/*.py`.
