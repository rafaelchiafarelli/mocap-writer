## 6. Fountain export raises IndexError on an empty title string

- **Status:** Fixed (2026-10-26) — fountain-native/io/5 (`5-one-fountain-path`): the code was deleted; Fountain import and export go through `fountain.load` / `generate`.
- **Symptom:** A title string with no items raises `IndexError`.
- **Where:** `titleLine.items[0]` (`trelby/screenplay.py:433`)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** export fails.
