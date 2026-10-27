## 1. Insert commands crash

- **Status:** Fixed (2026-10-26) — fixes/000086/one-line-crashes
- **Symptom:** Character map → Insert, Name database → Insert and Edit → Insert non-breaking space raise `AttributeError`.
- **Where:** they pass `util.MyKeyEvent` to `MyCtrl.OnKeyChar` (`trelby/charmapdlg.py:27`, `trelby/namesdlg.py:207`, `trelby/trelbyctrl.py:995`), whose `util.eventKeyCode` calls `ev.GetUnicodeKey()` (`trelby/trelbyctrl.py:1369`, `trelby/util.py:210`); `MyKeyEvent` has no such method (`trelby/util.py:789-810`)
- **Reproduce:** open Tools → Character map, pick a character, Insert.
- **Impact:** three menu commands do nothing but raise.
- **Likely fix:** give `MyKeyEvent` a `GetUnicodeKey`.
