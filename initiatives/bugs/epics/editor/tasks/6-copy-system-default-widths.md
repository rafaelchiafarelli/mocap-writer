## 6. Formatted copy uses default widths

- **Status:** Fixed (2026-10-27) — fixes/00008d/editor-small
- **Symptom:** Copy to system clipboard (formatted) lays text out with default element widths, not the script's.
- **Where:** `OnCopySystem` builds a fresh `Screenplay(self.gd.cfgGl)` without the script's `Config` (`trelby/trelbyctrl.py:858-868`)
- **Reproduce:** change Action width in script settings, copy formatted, paste in a text editor.
- **Impact:** pasted layout differs from the script.
- **Likely fix:** copy the script's `cfg` into the temporary screenplay.
- **Fix:** the temporary screenplay gets a copy of the script's `Config`. The widths were never the visible problem (the copied lines are already wrapped by the script); the indents and styles were.
