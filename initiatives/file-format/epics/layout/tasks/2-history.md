## 2. History and snapshots

- **Status:** Done (2026-10-28) — Rafael decided without a written study:
  the change log (below)
- **Type:** study (no code); Rafael decides
- **Depends on:** layout/1
- **Contract:**
  - In: a film root is not a git repository (study/1); preprod-link
    sync/1 keeps its own last-sync snapshot
  - Requires: two or three ways for option A to keep history inside the
    film root (e.g. a snapshot of the records on each accepted sync; the
    previous version kept per record; every change written as a Harpia
    message, which is the step toward C), each with its size on disk, how
    an agent pass is undone, and how it serves Sync to spec
  - Delivers: Rafael's decision, recorded here with the date, and the
    tasks it implies (and whether preprod-link sync/1 changes)
- **Pre-work:** —
- **Out of scope:** implementation
- **Tests:** —

### Decided: a change log (Rafael, 2026-10-28)

Of the three ways (a snapshot of the records on each accepted sync; the
previous version kept per record; every change written as a Harpia
message), the **change log**: every record the writer creates, changes or
deletes appends one `Change` message (time, who, record path and id, the
operation, the record before and after) to
`history/<yyyy-mm>.jsonl`, one JSON object per line. An agent pass is
undone by reverting its changes, newest first, filtered by `by`. On disk
it costs the text of the records changed, not a copy of the film; and it
is the log option C keeps in SQLite, so moving to C copies it. Not
chosen: a snapshot per sync (the film's size on every sync, sync points
only); the previous version per record (one undo step, no film-wide
view).

**Tasks it implies:** a `mocap-contracts` `change.harpia` (the `Change`
message, in `film-records`, `v0.5.0`); `layout/5` (the writer appends and
reverts). preprod-link sync/1 is unchanged: its snapshot is the last
synced state Sync to spec diffs against, not history.
