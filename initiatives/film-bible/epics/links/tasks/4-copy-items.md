## 4. Copy items

- **Type:** code
- **Depends on:** links/1–3
- **Contract:**
  - In: an item and a target (same film, or another film root)
  - Requires: a copy gets a new id and is unlinked by default; copying to
    another film copies the folder with its files and children, **without
    its scene links** (a scene number names a scene only in its own film,
    fountain-native/scenes/1); placing a
    copy into a scene, or removing an item that scenes still use, **warns**
    the creator and names the scenes affected
  - Delivers: copy inside a film and between films, with the warnings
- **Pre-work:** a second neutral film root as a fixture
- **Out of scope:** merging two items
- **Tests:** copy keeps files and children with new ids; cross-film copy
  drops the scene links;
  warning lists the scenes
