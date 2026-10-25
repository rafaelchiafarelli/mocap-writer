## 4. Tests off `.trelby`, then delete its code

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
