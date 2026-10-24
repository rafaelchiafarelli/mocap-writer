## 17. Text dialogs crash (`wx.TE_LINEWRAP`)

- **Status:** Fixed (2026-10-24) — fixes/000069/textdlg-linewrap
- **Symptom:** every `misc.TextDlg` raised `AttributeError: module 'wx' has no attribute 'TE_LINEWRAP'` before it showed: the warnings after loading a script (`misc.showText`, `trelby/trelbyctrl.py:144`) and the PDF import report never appeared, and the PDF import was lost.
- **Where:** `trelby/misc.py:914`, a wxPython 3 flag removed in wxPython 4.
- **Reproduce:** File → Import a PDF on the pdf-import branch (Rafael, 2026-10-24); the traceback is in the `docker/run.sh` output.
- **Impact:** high: blocked pdf-import/importer/1 and hid script-load warnings.
- **Fix:** `wx.TE_WORDWRAP`; `tests/test_wxnames.py` checks that every `wx.` name used in `trelby/` exists in the installed wxPython.
