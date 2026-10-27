# locales — compiled translation catalogs

**Role:** gettext `.mo` files, one per language: `en/LC_MESSAGES/trelby.mo`,
`it/LC_MESSAGES/trelby.mo`.
**Entry points:** `translations.trelby_translations_load()`
(`trelby/translations.py:10`) loads `trelby.mo` for `$LANG`, its base
language (`it_IT.UTF-8` → `it`), or `en`, and installs `_`.
**Inputs → Outputs:** `../../po/*.po` → `msgfmt` (`../../t_03_build.sh`) →
these files → translated GUI strings.

## Files
- `en/LC_MESSAGES/trelby.mo` — English catalog.
- `it/LC_MESSAGES/trelby.mo` — Italian catalog.

## Key facts / gotchas
- Build products committed to git: edit `po/<lang>.po`, then run
  `../../t_03_build.sh` from the repository root; never edit the `.mo`.
- `gettext.translation(...)` is called without `fallback=True`
  (`trelby/translations.py:25`): if `en` were missing, startup would fail.
- A translation must keep its message's `{}` placeholders: messages are
  formatted after the lookup (`../../po/CLAUDE.md`).

## Touchpoints
- Called by: `trelby/translations.py`.
- Built from: `po/` by `t_03_build.sh`.
