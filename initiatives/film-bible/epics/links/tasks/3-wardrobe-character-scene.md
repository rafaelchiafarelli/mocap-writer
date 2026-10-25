## 3. Wardrobe ↔ character × scene

- **Type:** code
- **Depends on:** maps/2, maps/4
- **Contract:**
  - In: a character in a scene
  - Requires: a wardrobe item links to (character id, scene number); a character
    in a scene without wardrobe is listed as a gap, not an error; a wardrobe
    item with no character is allowed
  - Delivers: the links and the gap list
- **Pre-work:** —
- **Out of scope:** continuity checks between scenes
- **Tests:** link, unlink, gap list, unlinked wardrobe
