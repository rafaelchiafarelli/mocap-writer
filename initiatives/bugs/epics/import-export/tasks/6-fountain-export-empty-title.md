## 6. Fountain export raises IndexError on an empty title string

- **Status:** Open
- **Symptom:** A title string with no items raises `IndexError`.
- **Where:** `titleLine.items[0]` (`trelby/screenplay.py:694`)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** export fails.
