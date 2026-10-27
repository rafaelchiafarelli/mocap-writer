## 5. Title keyword pattern `[A-za-z]`

- **Status:** Fixed (2026-10-26) — fountain-native/io/5 (`5-one-fountain-path`): the code was deleted; Fountain import and export go through `fountain.load` / `generate`.
- **Symptom:** The range `A-z` also matches `[ \ ] ^ _` and the backtick.
- **Where:** `trelby/screenplay.py:427` (export) and `trelby/myimport.py:503` (import)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** rare misread title lines.
- **Likely fix:** `[A-Za-z]`.
