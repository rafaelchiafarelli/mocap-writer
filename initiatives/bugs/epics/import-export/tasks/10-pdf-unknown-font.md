## 10. Unknown custom PDF font raises an uncaught Exception

- **Status:** Open
- **Symptom:** A custom font name with no file raises a plain `Exception` that callers do not catch.
- **Where:** `trelby/pdf.py:325-333`
- **Reproduce:** set a PDF font name with no file, export PDF.
- **Impact:** traceback instead of a message.
