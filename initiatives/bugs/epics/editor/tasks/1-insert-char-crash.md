## 1. Insert commands crash

- **Status:** Open
- **Symptom:** Character map → Insert, Name database → Insert and Edit → Insert non-breaking space raise `AttributeError`.
- **Where:** they pass `util.MyKeyEvent` to `MyCtrl.OnKeyChar` (`trelby/charmapdlg.py:27`, `trelby/namesdlg.py:207`, `trelby/trelbyctrl.py:901`), which calls `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1275`); `MyKeyEvent` has no such method (`trelby/util.py:776-797`)
- **Reproduce:** open Tools → Character map, pick a character, Insert.
- **Impact:** three menu commands do nothing but raise.
- **Likely fix:** give `MyKeyEvent` a `GetUnicodeKey`.
