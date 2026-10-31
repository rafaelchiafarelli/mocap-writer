# tools — maintenance scripts

**Role:** developer scripts: one from upstream Trelby, ported to Python 3
and the current layout (2026-10-27), and the fixture film other
repositories test with (2026-10-31).
**Entry points:** `tools/add_words.py`, run by hand from any directory
(paths relative to the script, `tools/add_words.py:9-10`);
`tools/make_fixture_film.py <empty-dir>`, run in the writer's image with
the repository root on `PYTHONPATH` (mocap-preprod's
`tools/make_fixture_film.sh` does that from a fresh clone).
**Inputs → Outputs:** words on the command line → `trelby/dict_en.dat`;
nothing → a neutral film root.

## Files
- `add_words.py` — `tools/add_words.py word1 word2...`: adds the words,
  lower-cased, to `trelby/dict_en.dat` (the English spell-checker word
  list), keeping it UTF-8, sorted and free of duplicates; prints how many
  were new (`tools/add_words.py:13-27`).
- `make_fixture_film.py` — a neutral film root made through the writer's
  own code, as a creator would: `Film.create`, bible items with values and
  scene links, the front matter, a note and a shot
  (`tools/make_fixture_film.py:65-107`), then a sync accepted on the first
  draft and on the edited one, which adds scene `2.A`, changes scene `3`
  and adds the prop word `KEY` (`:109`, `:114`). Used by mocap-preprod's
  tests; checked here by `tests/test_fixture_film_tool.py`.

## Key facts / gotchas
- `spellcheck.loadDict` reads the plain `dict_en.dat`; a `.gz` is read
  only when the plain file is missing (`loadMaybeCompressedFile`,
  `trelby/util.py:1042-1051`), and nothing builds one any more.
- `update_icns.py` (the macOS icon) was removed with `resources_mac/`
  (2026-10-31).

## Touchpoints
- Writes: `trelby/dict_en.dat` (`add_words.py`); a film root in the
  directory given (`make_fixture_film.py`).
- Read by: mocap-preprod `tools/make_fixture_film.sh` (clones this
  repository and runs the script).
