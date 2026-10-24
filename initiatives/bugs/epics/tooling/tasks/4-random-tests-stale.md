## 4. execute_random_tests.py uses the old layout

- **Status:** Open
- **Symptom:** It imports `u` and `screenplay` as top-level modules.
- **Where:** `tests/execute_random_tests.py:16-20`
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** the script doesn't run.
