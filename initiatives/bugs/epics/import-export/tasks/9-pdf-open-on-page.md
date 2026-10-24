## 9. "Open PDF on current page" has no effect

- **Status:** Open
- **Symptom:** The setting is shown but the PDF writer ignores it.
- **Where:** `/OpenAction` is commented out (`trelby/pdf.py:266-269`); page `trelby/configpages/pdfpanel.py:26`
- **Reproduce:** turn it on, print.
- **Impact:** dead setting.
- **Likely fix:** remove the setting or document it as unsupported.
