## 7. Non-Latin-1 text in a Helvetica/Times title page raises IndexError

- **Status:** Open
- **Symptom:** A character above U+00FF in a title string in Helvetica or Times raises `IndexError`; typed input is filtered to Latin-1 (`trelby/util.py:206`) but paste and import are not.
- **Where:** `FontMetrics.getTextWidth` indexes a 256-entry table with `ord(ch)` (`trelby/fontinfo.py:57-60`)
- **Reproduce:** paste "Ł" into a title string, export PDF.
- **Impact:** PDF export fails.
