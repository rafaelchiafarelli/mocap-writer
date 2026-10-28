## 3. Prop (item cênico) editor

- **Status:** Done (2026-10-28) — the generic form of maps/1 (`trelby/bibleform.py`), generated from this map's catalog; `tests/test_bibleedit.py` covers this map

- **Type:** code
- **Depends on:** tree/1
- **Contract:**
  - In: one props item selected in the tree
  - Requires: a form with the approved catalog's fields for this map, grouped
    as in the catalog; each value shows its state and lets the creator approve
    a `proposal`; files (photos, plans, `.blend`) are added by drag and drop
    and copied into the item's folder; the form is generated from the
    catalog, so a catalog change needs no new form code
  - Delivers: the props editor
- **Pre-work:** —
- **Out of scope:** links to scenes (links epic)
- **Tests:** every catalog field of this map appears; edit → save → reopen;
  approving a proposal changes its state only
