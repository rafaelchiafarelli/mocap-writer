## 1. Tab order

- **Status:** Done (2026-10-24) — `ConfigGlobal.tabOrder` (saved as
  `TabOrder`, default Scene → Action → Character → Dialogue) with
  `nextTypeTab(lt)` / `prevTypeTab(lt)`; the per-type `nextTypeTab` /
  `prevTypeTab` fields and their two Settings → Elements combos are gone.
  **Decided in implementation, for Rafael to check:** an element outside
  the cycle (Paren, Transition, Shot, Act break, Note) goes to Action on
  both Tab and Shift+Tab; Tab at the end of an element still creates
  `newTypeTab` (unchanged); the cycle has no settings page (config file
  only). `tests/test_taborder.py`, `tests/test_changetype.py`

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
