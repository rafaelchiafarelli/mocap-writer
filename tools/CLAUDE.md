# tools — maintenance scripts

**Role:** A developer script from upstream Trelby, ported to Python 3 and
the current layout (2026-10-27). Not used by the tests or Docker.
**Entry points:** run by hand, from any directory: paths are relative to
the script (`tools/add_words.py:9-10`).
**Inputs → Outputs:** words on the command line → `trelby/dict_en.dat`.

## Files
- `add_words.py` — `tools/add_words.py word1 word2...`: adds the words,
  lower-cased, to `trelby/dict_en.dat` (the English spell-checker word
  list), keeping it UTF-8, sorted and free of duplicates; prints how many
  were new (`tools/add_words.py:13-27`).

## Key facts / gotchas
- `spellcheck.loadDict` reads the plain `dict_en.dat`; a `.gz` is read
  only when the plain file is missing (`loadMaybeCompressedFile`,
  `trelby/util.py:1042-1051`), and nothing builds one any more.
- `update_icns.py` (the macOS icon) was removed with `resources_mac/`
  (2026-10-31).

## Touchpoints
- Writes: `trelby/dict_en.dat`.
