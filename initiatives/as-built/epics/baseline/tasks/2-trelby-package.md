## 2. The trelby/ package

- **Type:** documentation (no code)
- **Depends on:** baseline/1
- **Contract:**
  - In: `trelby/*.py`
  - Requires: `trelby/CLAUDE.md` in the harpia format with one bullet per
    module (all 55); `<module>.as-built.md` next to `screenplay.py`,
    `trelbyctrl.py`, `config.py`, `viewmode.py`, `myimport.py` and `pdf.py`:
    classes and key functions with `file:line`, data structures and their
    invariants, extension points the planned initiatives touch (element
    types and Tab table, colors, screen fonts, import, Fountain export),
    gotchas, the tests that cover the module
  - Delivers: those seven files
- **Pre-work:** —
- **Out of scope:** the other folders (task 3)
- **Tests:** every module in `trelby/` has a bullet; every `file:line`
  resolves
