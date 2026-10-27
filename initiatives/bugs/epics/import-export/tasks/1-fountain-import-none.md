## 1. Fountain import of an empty or unreadable file raises TypeError

- **Status:** Fixed (2026-10-26) — fountain-native/io/5 (`5-one-fountain-path`): the code was deleted; Fountain import and export go through `fountain.load` / `generate`.
- **Symptom:** Importing an empty `.fountain` raises `TypeError` after the "File is empty" box.
- **Where:** `importFountain` returns a bare `None` (`trelby/myimport.py:442-447`); the caller unpacks two values (`trelby/trelbyctrl.py:207-209`)
- **Reproduce:** File → Import an empty `.fountain`.
- **Impact:** traceback instead of a clean stop.
- **Likely fix:** return `(None, titlePages)` as the cancel path does.
