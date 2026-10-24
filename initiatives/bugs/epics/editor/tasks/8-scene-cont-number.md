## 8. Scene CONTINUED number differs between screen and PDF

- **Status:** Open
- **Symptom:** In layout and side-by-side modes `CONTINUED (2)` numbers can differ from the PDF.
- **Where:** `pager.sceneContNr` is reset on every page (`trelby/viewmode.py:342-345`, `trelby/viewmode.py:455-458`)
- **Reproduce:** a scene longer than two pages with scene continueds on.
- **Impact:** screen preview only.
