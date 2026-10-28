## 2. Bible folders and contract

- **Status:** Done (2026-10-28) — `mocap-contracts` `v0.5.0`
  (`bible.harpia`, `catalog/bible-v1.json`); `trelby/bible.py`

- **Type:** code, here and in `mocap-contracts`
- **Depends on:** contract/1 (approved catalog); a `mocap-contracts` task for
  `bible.harpia` done and tagged; fountain-native/scenes/1 (scene numbers);
  file-format/layout/1 (root index, id scheme)
- **Contract:**
  - In: the approved catalog
  - Requires: `<film-root>/bible/<map>/<item-slug>/` per item, holding
    `item.json` (a `bible.harpia` message: id, map, fields with state and
    source), its files (`photos/`, `plans/`, `blend/`) and child item folders;
    `bible/` is a part listed in `film.json`; ids follow the layout/1 scheme
    and are independent of the folder name; references to scenes
    use scene numbers; a field not in the catalog is refused, not stored
  - Delivers: read/write library for the bible, used by the editor and by
    other repositories
- **Pre-work:** the `mocap-contracts` task above
- **Out of scope:** UI
- **Tests:** write → read round trip per map; child items; unknown field
  refused; rename the folder and the id still resolves

### Decided (Rafael, 2026-10-28)

- **Generic items plus the catalog as data**, not one typed message per
  map: `bible.harpia` has one `BibleItem` (id, name, aliases, parent,
  values, scene links), each value a `BibleValue` (catalog field, the
  scene for a per-scene group, the value, state, source, department, by,
  revisit trigger); the approved catalog (contract/1) is a `BibleCatalog`
  message shipped in `mocap-contracts` (`catalog/bible-v1.json`), and the
  rules refuse a field it doesn't list or a value of the wrong type. A
  catalog change is a data change: the editor's forms are built from it
  (maps/1–4).
- **Map folders** in English, as the record kinds: `bible/sets/`,
  `bible/characters/`, `bible/props/`, `bible/wardrobe/`.
- **Item folders** are an ASCII slug of the name: `Xícara Azul` →
  `xicara-azul`, `-2`, `-3`... on a clash; renaming the item renames its
  folder; the id inside `item.json` never changes.
- A child item is a folder inside its parent's folder, of the same map,
  and its `item.json` names the parent's id.
- The film-wide "not a prop" words (links/2) are a `NotProps` message in
  `bible/not-props.json`.
- `mocap-contracts` work approved (Rafael, 2026-10-28): `bible.harpia`
  with the catalog in its `film-records` initiative, released in `v0.5.0`.
