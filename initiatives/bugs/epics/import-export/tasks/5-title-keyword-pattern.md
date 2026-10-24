## 5. Title keyword pattern `[A-za-z]`

- **Status:** Open
- **Symptom:** The range `A-z` also matches `[ \ ] ^ _` and the backtick.
- **Where:** `trelby/screenplay.py:683` (export) and `trelby/myimport.py:503` (import)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** rare misread title lines.
- **Likely fix:** `[A-Za-z]`.
