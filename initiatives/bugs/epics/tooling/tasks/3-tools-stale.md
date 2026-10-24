## 3. tools/ scripts are stale

- **Status:** Open
- **Symptom:** `add_words.py` is Python 2 for the old layout; `update_icns.py` reads `../resources`, which no longer exists.
- **Where:** `tools/add_words.py:9-12`, `tools/add_words.py:34-36`, `tools/update_icns.py:7`
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** the scripts don't run.
- **Likely fix:** fix or remove.
