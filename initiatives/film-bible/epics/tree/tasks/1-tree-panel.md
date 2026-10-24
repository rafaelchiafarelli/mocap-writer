## 1. Tree panel

- **Type:** code
- **Depends on:** contract/2
- **Contract:**
  - In: the film root's `bible/`
  - Requires: a side panel with one tree per map (sets, characters, props,
    wardrobe), like Windows Explorer: expand, select, create, rename, delete
    (with confirmation), drag a child item into another item; selecting an
    item opens its editor (maps epic); the script editor stays usable next to
    it
  - Delivers: the panel
- **Pre-work:** —
- **Out of scope:** item editors (maps), links (links)
- **Tests:** the tree matches the folders; create/rename/delete/move change
  the folders and keep ids
