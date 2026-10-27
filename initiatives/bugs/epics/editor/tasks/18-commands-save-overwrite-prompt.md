## 18. Help → Commands → Save crashes (`wx.OVERWRITE_PROMPT`)

- **Status:** Fixed (2026-10-26) — fixes/000086/one-line-crashes
- **Symptom:** saving the commands list as HTML should raise `AttributeError: module 'wx' has no attribute 'OVERWRITE_PROMPT'`.
- **Where:** `trelby/commandsdlg.py:94`; wxPython 4 names it `wx.FD_OVERWRITE_PROMPT`.
- **Reproduce:** found by a scan of the `wx.` names used in `trelby/` (fixes/000069); not run in the GUI.
- **Impact:** low: the commands list cannot be saved.
- **Fix:** `wx.FD_OVERWRITE_PROMPT`; then remove it from the known list in `tests/test_wxnames.py`.
