## 3. Import picks the format by a case-sensitive suffix

- **Status:** Fixed (2026-10-27) — fixes/00008c/import-export-small
- **Symptom:** `SCRIPT.FDX` is imported as plain text; any name ending in `fdx` without a dot is read as FDX.
- **Where:** `fileName.endswith("fdx")` etc. (`trelby/trelbyctrl.py:219-229`)
- **Reproduce:** import a file named `SCRIPT.FDX`.
- **Impact:** wrong importer, garbage result.
- **Likely fix:** compare the lower-cased extension.
