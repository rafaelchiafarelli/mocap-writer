## 13. Arrow keys steal the keyboard

- **Status:** Fixed (2026-10-24) — fixes/000066/arrow-keys-steal-focus
- **Symptom:** Arrows, Home, End, Page Up/Down and F-keys did not move the cursor; after one of them the keyboard focus jumped to the tab bar, typing stopped, and a click in the script did not bring it back (only menu shortcuts such as Ctrl+Z / Ctrl+Y kept working).
- **Where:** `MyCtrl.OnKeyChar` took the key code from `ev.GetUnicodeKey()` (upstream "Fix for #89", commit `ded2305`), which is `WXK_NONE` for keys that are not characters: no command matched, the event was skipped and GTK moved the focus with the arrow. `MyCtrl.OnLeftDown` never set the focus.
- **Reproduce:** press an arrow key in the script (Rafael, 2026-10-24; an instrumented session logged `uni=0` and the focus moving to `MyTabCtrl2`).
- **Impact:** critical: the writer loses the keyboard.
- **Fix:** `util.eventKeyCode` falls back to `GetKeyCode()` when there is no Unicode value; a click in the script sets the focus (`tests/test_keycode.py`).
