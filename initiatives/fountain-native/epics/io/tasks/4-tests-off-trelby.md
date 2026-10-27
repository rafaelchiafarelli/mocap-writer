## 4. Tests off `.trelby`, then delete its code

- **Status:** Done (2026-10-25) — `tests/fixtures/test.fountain` +
  `test.sconf` replace `test.trelby` (lines identical up to the ending);
  `Screenplay.load` / `save`, `getConfigPart`, `parseConfigLine`,
  `fileformat.txt` and the fixture deleted; 148 tests (one split in two).
- **Expected values changed:** the ending Fountain cannot hold ("Very." as
  its own dialogue, two empty Actions, "Very" as an orphan dialogue)
  becomes one dialogue "Very.\nVery", so the last line is 159, not 161:
  `testMoveRight`, `testMoveLeft`, `testMoveEnd`, `testMoveSceneDown`.
  `testMoveNextWord`, `testMovePrevWord` (they step through the empty lines)
  and `testImportCeltx` (`test.celtx` has the old ending) put the old ending
  back with `u.withOldEnding` and check exactly what they did before.

- **Type:** code (tests)
- **Depends on:** io/3
- **Contract:**
  - In: `tests/fixtures/test.trelby` and the tests that load it through
    `tests/u.py`
  - Requires: the fixture becomes a `.fountain` (plus whatever per-script
    settings the tests rely on, set in code), every test keeps checking the
    same behaviour (line and cursor positions may need new expected
    values, each change explained in the commit); then `Screenplay.load` /
    `save`, `fileformat.txt` and the fixture are deleted
  - Delivers: no `.trelby` code left
- **Pre-work:** —
- **Out of scope:** changing what any test checks
- **Tests:** the full suite, same count
