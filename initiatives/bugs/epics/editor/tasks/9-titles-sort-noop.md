## 9. Titles.sort() does nothing

- **Status:** Open
- **Symptom:** Title strings are never sorted.
- **Where:** `sort` rebinds a local, and its compare has `(a.x < a.y)` for `(a.x < b.x)` (`trelby/titles.py:58-61`)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** title-page RTF/PML output keeps insertion order.
- **Likely fix:** sort in place and fix the compare.
