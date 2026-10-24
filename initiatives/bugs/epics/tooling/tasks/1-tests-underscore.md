## 1. A single test file fails on its own

- **Status:** Open
- **Symptom:** `docker/test.sh tests/test_cut.py` fails with `NameError: name '_' is not defined` (6 failures; with `test_myimport.py`, 8).
- **Where:** only `tests/test_validate.py:5` installs `_`
- **Reproduce:** run one test file.
- **Impact:** can't run tests selectively.
- **Likely fix:** install `_` in `tests/u.py` or a `conftest.py`.
