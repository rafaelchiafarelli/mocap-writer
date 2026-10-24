## 2. Exit "save" saves only the current tab

- **Status:** Open
- **Symptom:** On exit with unsaved changes, answering Save saves the current tab only; other modified tabs are lost.
- **Where:** `MyFrame.OnCloseWindow` calls `self.OnSave()` once (`trelby/trelbyframe.py:989-990`)
- **Reproduce:** edit two tabs, exit, choose Save.
- **Impact:** data loss in every tab but the current one.
- **Likely fix:** save (or ask for) each modified tab.
