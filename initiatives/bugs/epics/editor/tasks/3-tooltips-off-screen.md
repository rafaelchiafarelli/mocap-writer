## 3. Toolbar tooltips start off-screen

- **Status:** Open
- **Symptom:** Tooltips of the vertical toolbar open partly outside the screen.
- **Where:** the toolbar is created with `wx.TB_VERTICAL` and tooltips come from `shortHelp` (`trelby/trelbyframe.py:190`, `trelby/trelbyframe.py:207-212`)
- **Reproduce:** hover a toolbar icon (seen in Rafael's review of unmodified Trelby, 2026-10-23; `initiatives/README.md`).
- **Impact:** cosmetic.
- **Likely fix:** not known yet; needs a look at a running app.
