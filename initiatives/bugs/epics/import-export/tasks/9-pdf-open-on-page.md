## 9. "Open PDF on current page" has no effect

- **Status:** Fixed (2026-10-27) — fixes/000091/pdf-open-on-page (implemented, Rafael 2026-10-27)
- **Symptom:** The setting is shown but the PDF writer ignores it.
- **Where:** `/OpenAction` is commented out (`trelby/pdf.py:268-271`); page `trelby/configpages/pdfpanel.py:26`
- **Reproduce:** turn it on, print.
- **Impact:** dead setting.
- **Likely fix:** remove the setting or document it as unsupported.
