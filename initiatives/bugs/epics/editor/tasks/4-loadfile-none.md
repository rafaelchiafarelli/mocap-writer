## 4. A read error on open shows a second, wrong error

- **Status:** Fixed (2026-10-25) — fountain-native/io/3 (`3-remove-trelby`): the
  `.trelby` read path was removed; the Fountain path checks `None`.
- **Symptom:** If a script cannot be read, the user also gets a "too few lines" error.
- **Where:** `MyCtrl.loadFile` wraps `util.loadFile` in `str(...)`, so `None` becomes `"None"` and the `None` check never fires (`trelby/trelbyctrl.py:151-153`)
- **Reproduce:** open a `.trelby` file without read permission (the `.fountain` path checks `None`, `trelby/trelbyctrl.py:130`).
- **Impact:** confusing message only.
- **Likely fix:** drop the `str(...)`.
