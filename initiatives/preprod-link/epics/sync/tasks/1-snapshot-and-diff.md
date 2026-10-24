## 1. Snapshot and diff

- **Type:** code
- **Depends on:** contract/1, contract/2
- **Contract:**
  - In: the open script, `<film-root>/bible/`
  - Requires: the last accepted index is kept at
    `<film-root>/bible/sync/last-sync.json`; a run builds the current index,
    diffs it against the snapshot and writes
    `<film-root>/bible/sync/<timestamp>-changes.json`; the snapshot advances
    only when the creator accepts the sync, so an unaccepted run can be
    repeated; the first run (no snapshot) reports every scene as added
  - Delivers: `sync_run()` / `sync_accept()` in the writer's library
- **Pre-work:** —
- **Out of scope:** UI (sync/2), affected records (sync/3)
- **Tests:** first run; edit → run → accept → run again gives an empty change
  set; run without accept twice gives the same change set
