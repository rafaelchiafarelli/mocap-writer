## 8. Watermarks with non-Latin characters come out wrong

- **Status:** Open
- **Symptom:** Rotated text goes through `addLiteral` + `escapeStr`.
- **Where:** `trelby/pdf.py:82` (TODO in the code)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** only for watermarked PDFs with such characters.
