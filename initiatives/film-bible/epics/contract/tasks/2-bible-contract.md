## 2. Bible folders and contract

- **Type:** code, here and in `mocap-contracts`
- **Depends on:** contract/1 (approved catalog); a `mocap-contracts` task for
  `bible.harpia` done and tagged; fountain-native/scenes/1 (scene ids)
- **Contract:**
  - In: the approved catalog
  - Requires: `<film-root>/bible/<map>/<item-slug>/` per item, holding
    `item.json` (a `bible.harpia` message: id, map, fields with state and
    source), its files (`photos/`, `plans/`, `blend/`) and child item folders;
    ids are stable and independent of the folder name; references to scenes
    use scene ids; a field not in the catalog is refused, not stored
  - Delivers: read/write library for the bible, used by the editor and by
    other repositories
- **Pre-work:** the `mocap-contracts` task above
- **Out of scope:** UI
- **Tests:** write → read round trip per map; child items; unknown field
  refused; rename the folder and the id still resolves
