## 2. Wrong line reference in tools/CLAUDE.md

- **Status:** Open
- **Symptom:** "writes `str` to a file opened in binary mode" cites `tools/add_words.py:30-32`, which sorts the list; the write is at `tools/add_words.py:34-36`.
- **Where:** `tools/CLAUDE.md:19`
- **Reproduce:** as-built review, 2026-10-24.
- **Impact:** one wrong pointer.
- **Likely fix:** change the reference.
