## 5. Change log

- **Type:** code, after a `mocap-contracts` task (`change.harpia`)
- **Depends on:** layout/1; layout/2 (decided: change log); `Change` in
  `mocap-contracts` `v0.5.0`
- **Contract:**
  - In: every record the writer writes or deletes through layout/1
  - Requires: one `Change` per write (`time` UTC ISO-8601, `by`, `path`
    relative to the film root, `record` id when the file has one, `op`
    create / update / delete, `before` and `after` the record's JSON text)
    appended to `history/<yyyy-mm>.jsonl`, one line each; a write that
    changes nothing logs nothing; **revert** of a list of changes, newest
    first, puts each record back to its `before`, and is itself logged;
    `changes(by=...)` lists one author's changes, so an agent pass can be
    undone
  - Delivers: logging inside the film library's writes; `changes` and
    `revert`
- **Pre-work:** —
- **Out of scope:** a UI for history; moving to C
- **Tests:** create, update, delete each log one line; an unchanged write
  logs none; revert of an author's changes restores the records and logs
  the revert
