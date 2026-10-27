## 5. Invalid escape sequences in titles.py

- **Status:** Fixed (2026-10-26) — fixes/000085/tests-standalone
- **Symptom:** `" \qc"` / `" \qr"` give a `SyntaxWarning` in every test run.
- **Where:** `trelby/titles.py:158-160`
- **Reproduce:** `docker/test.sh`.
- **Impact:** noise; a future Python makes it an error.
- **Fix:** raw strings.
