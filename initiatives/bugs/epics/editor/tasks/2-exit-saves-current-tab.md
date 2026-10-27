## 2. Exit "save" saves only the current tab

- **Status:** Fixed (2026-10-26) — fixes/000084/exit-save-all-tabs
- **Symptom:** On exit with unsaved changes, answering Save saves the current tab only; other modified tabs are lost.
- **Where:** `MyFrame.OnCloseWindow` calls `self.OnSave()` once (`trelby/trelbyframe.py:1000-1001`)
- **Reproduce:** edit two tabs, exit, choose Save.
- **Impact:** data loss in every tab but the current one.
- **Fix:** `MyFrame.saveAll` saves each modified tab, selecting it first; if one stays modified (Save As cancelled, write error) the exit is called off (`tests/test_saveall.py`).
