## 1. Tab order

- **Type:** code
- **Depends on:** —
- **Contract:**
  - In: Tab / Shift+Tab on an empty or current line
  - Requires: Tab cycles Scene → Action → Character → Dialogue → Scene;
    Shift+Tab goes back; the order is a list in the config, not hard-coded per
    element (today each type has its own `nextTypeTab`); Enter rules stay as
    they are
  - Delivers: the new cycle; the menu keeps showing each element's shortcut
- **Pre-work:** —
- **Out of scope:** smarter rules (they come when there are more elements)
- **Tests:** a full Tab cycle and a full Shift+Tab cycle; the upstream
  `test_changetype.py` updated to the new order
