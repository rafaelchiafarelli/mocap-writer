## 2. Change set

- **Status:** Done (2026-10-31) — `trelby/changeset.py` (`diff`), `mocap-contracts` `v0.7.0` (`change_set.harpia`).
- **Type:** code, here and in `mocap-contracts`
- **Depends on:** contract/1; a `mocap-contracts` task for a `change_set`
  message, done and tagged
- **Contract:**
  - In: two scene indexes (last sync, now)
  - Requires: scenes matched by scene number, never by heading or position; each
    change typed (scene added, removed, moved, heading changed, text changed,
    character entered/left, prop word added/removed, set link changed) with
    the scene number and old/new values; the change set records the two index
    hashes it was made from
  - Delivers: the `change_set` message and a pure diff function
- **Pre-work:** the `mocap-contracts` task above
- **Out of scope:** where snapshots live and when they advance (sync/1);
  which records are affected (sync/3)
- **Tests:** one test per change type; a moved and edited scene reports both;
  identical indexes → empty change set
