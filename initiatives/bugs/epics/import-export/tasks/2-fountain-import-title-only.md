## 2. Fountain import of a title-only file raises IndexError

- **Status:** Open
- **Symptom:** A file that is only a title block, with no blank line and no final newline, raises `IndexError`.
- **Where:** `prelines[titleIdx]` without a bounds check (`trelby/myimport.py:518-531`)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** import fails on that edge case.
