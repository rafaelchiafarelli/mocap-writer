## 10. Test-mode hotkeys collapsed

- **Status:** Open
- **Symptom:** With `--test`, only the first test hotkey (load `trelby/sample.fountain`, `sample.trelby` until 2026-10-25) works.
- **Where:** the three characters became U+FFFD (`trelby/trelbyctrl.py:1387-1392`)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** test mode only.
