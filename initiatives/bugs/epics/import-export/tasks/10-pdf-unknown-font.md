## 10. Unknown custom PDF font raises an uncaught Exception

- **Status:** Fixed (2026-10-27) — fixes/00008c/import-export-small
- **Symptom:** A custom font name with no file raises a plain `Exception` that callers do not catch.
- **Where:** `trelby/pdf.py:327-335`
- **Reproduce:** set a PDF font name with no file, export PDF.
- **Impact:** traceback instead of a message.
