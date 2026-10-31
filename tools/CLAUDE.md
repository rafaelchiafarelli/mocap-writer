# tools — maintenance scripts

**Role:** Two developer scripts from upstream Trelby, ported to Python 3
and the current layout (2026-10-27). Neither is used by the build, the
tests or Docker.
**Entry points:** run by hand, from any directory: paths are relative to
the script (`tools/add_words.py:9-10`, `tools/update_icns.py:10-12`).
**Inputs → Outputs:** see each file.

## Files
- `add_words.py` — `tools/add_words.py word1 word2...`: adds the words,
  lower-cased, to `trelby/dict_en.dat` (the spell checker's word list),
  keeping it UTF-8, sorted and free of duplicates; prints how many were new
  (`tools/add_words.py:13-27`).
- `update_icns.py` — builds `resources_mac/icon.icns` from
  `trelby/resources/icon*.png` with the `icnsutil` package (MIT), skipping
  a PNG icnsutil cannot place (`icon64.png`).

## Key facts / gotchas
- `icnsutil` is not in `docker/requirements.lock`: install it where the
  script runs (`pip install icnsutil`). Checked 2026-10-27 in a throwaway
  container: the output has the size of the committed `icon.icns`.
- `trelby/dict_en.dat.gz`, if built (`make dist`), is not refreshed by
  `add_words.py`; `spellcheck.loadDict` reads the plain file when it
  exists (`loadMaybeCompressedFile`, `trelby/util.py:1042-1051`).

## Touchpoints
- Writes: `trelby/dict_en.dat`, `resources_mac/icon.icns`.
