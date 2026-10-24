## 4. A read error on open shows a second, wrong error

- **Status:** Open
- **Symptom:** If a script cannot be read, the user also gets a "too few lines" error.
- **Where:** `MyCtrl.loadFile` wraps `util.loadFile` in `str(...)`, so `None` becomes `"None"` and the `None` check never fires (`trelby/trelbyctrl.py:127-129`)
- **Reproduce:** open a file without read permission.
- **Impact:** confusing message only.
- **Likely fix:** drop the `str(...)`.
