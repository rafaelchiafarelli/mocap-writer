# tools — upstream maintenance scripts

**Role:** Two one-off developer scripts from upstream Trelby. Neither is
used by the build, the tests or Docker.
**Entry points:** run by hand from inside `tools/`.
**Inputs → Outputs:** see each file.

## Files
- `add_words.py` — adds the words given on the command line to
  `../dict_en.dat`, keeping it sorted and lower-case.
- `update_icns.py` — builds `../resources_mac/icon.icns` from
  `../resources/icon*.png` with the `icnsutil` package.

## Key facts / gotchas
- **Both are stale.** `add_words.py` is Python 2 code for the old layout:
  it puts `../src` on `sys.path` and imports `misc` / `util` as top-level
  modules (`tools/add_words.py:9-12`), reads `../dict_en.dat` (now
  `trelby/dict_en.dat`) and writes `str` to a file opened in binary mode
  (`tools/add_words.py:30-32`). `update_icns.py` reads `../resources`
  (`tools/update_icns.py:7`), but the icons are in `trelby/resources/`.
- `icnsutil` is not in `docker/requirements.lock`.

## Touchpoints
- Writes: `trelby/dict_en.dat` (meant to), `resources_mac/icon.icns`.
