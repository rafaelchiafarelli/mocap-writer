## 8. Watermarks with non-Latin characters come out wrong

- **Status:** Fixed (2026-10-31) — fixes/0000ad/watermark-non-latin
- **Symptom:** Rotated text goes through `addLiteral` + `escapeStr`.
- **Where:** `trelby/pdf.py:64-76` (was a literal `Tj` block with a TODO)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** only for watermarked PDFs with such characters.
