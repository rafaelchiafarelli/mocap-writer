## 6. Formatted copy uses default widths

- **Status:** Open
- **Symptom:** Copy to system clipboard (formatted) lays text out with default element widths, not the script's.
- **Where:** `OnCopySystem` builds a fresh `Screenplay(self.gd.cfgGl)` without the script's `Config` (`trelby/trelbyctrl.py:790-798`)
- **Reproduce:** change Action width in script settings, copy formatted, paste in a text editor.
- **Impact:** pasted layout differs from the script.
- **Likely fix:** copy the script's `cfg` into the temporary screenplay.
