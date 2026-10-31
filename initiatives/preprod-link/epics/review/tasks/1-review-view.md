## 1. Review view

- **Status:** Done (2026-10-31) — `trelby/review.py`, `trelby/reviewdlg.py` (Script → Review proposals…, and Review… in the Sync panel); reject puts back the replaced value from the change log; checked through the real window.
- **Type:** code (UI)
- **Depends on:** film-bible/maps; sync/3
- **Contract:**
  - In: `<film-root>/bible/`
  - Requires: every value in state `proposal` or `TBD`, and every value listed
    as needs review, shown in one queue grouped by scene (and by item for
    values that don't depend on a scene); approve, reject or edit from the
    keyboard, one at a time or a selected batch; approving sets
    `creator-approved` and keeps the proposal's source; an item-level value
    shows the scenes it applies to, so it is decided once
  - Delivers: the review view
- **Pre-work:** —
- **Out of scope:** the agents writing proposals (epics/agents); story notes
- **Tests:** batch approve keeps sources; reject removes the proposal and
  leaves the previous value; a per-scene override shown under its scene only
