## 1. Scene index

- **Type:** code, here and in `mocap-contracts`
- **Depends on:** fountain-native/scenes/1 (scene numbers); film-bible/contract/2
  (bible library, to resolve known characters and props);
  file-format/layout/1 (the index is a file of the writer's `bible`
  part, Rafael 2026-10-26); a
  `mocap-contracts` task for a `scene_index` message, done and tagged
- **Contract:**
  - In: the open script (Fountain) and `<film-root>/bible/`
  - Requires: one entry per scene with its scene number (its identity), order,
    heading parts (INT/EXT, set name as written, time of day), the bible set
    id it links to (if linked), speaking characters and characters named in
    Action (bible ids when known, the written name otherwise), prop words
    (bible ids when known), page and line range, and a hash of the scene's
    text; computed by code only, nothing inferred beyond the script and the
    existing links
  - Delivers: `<film-root>/bible/scene-index.json` (a `scene_index` message)
    and the library function that builds it
- **Pre-work:** the `mocap-contracts` task above
- **Out of scope:** diffing (contract/2, sync/1), UI
- **Tests:** neutral sample → expected index; an unlinked set and an unknown
  name kept as written; same script twice → identical file
