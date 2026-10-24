## 1. trelby.process.md

- **Status:** Done (2026-10-24) — `trelby.process.md`, 146 `file:line`
  references checked
- **Type:** documentation (no code)
- **Depends on:** —
- **Contract:**
  - In: the code at the fork baseline (`dev`)
  - Requires: stages, in the order they run: startup (`trelby.py` →
    `trelby.main`, `misc.init`, config load, splash), main window and editor,
    the screenplay model (lines, elements, pages), editing and keyboard
    (Enter/Tab rules), screen rendering (`viewmode`), save/open (`.trelby`),
    import (`myimport`), export (Fountain, PDF, others), reports; every stage
    with its entry point as `file:line`
  - Delivers: `trelby.process.md` at the repository root
- **Pre-work:** —
- **Out of scope:** per-module detail (tasks 2 and 3)
- **Tests:** every `file:line` reference resolves
