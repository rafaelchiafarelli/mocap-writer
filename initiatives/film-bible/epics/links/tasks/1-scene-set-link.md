## 1. Scene ↔ set

- **Status:** Done (2026-10-28) — `biblelinks.setPlan`, From script → Link
  scenes to sets; shown in the set's form (Scenes) and in the panel's
  scene line for the cursor's scene

- **Type:** code
- **Depends on:** maps/1
- **Contract:**
  - In: a scene heading's location (`INT. SALA DE JANTAR - NOITE` → `SALA DE JANTAR`)
  - Requires: a location not in the sets map offers to create the set (never
    silently); a known location links the scene number to that set; a set with no
    scene is allowed (made ahead of time, placed later)
  - Delivers: the link, shown in both the scene and the set
- **Pre-work:** —
- **Out of scope:** INT/EXT prefixes
- **Tests:** new location → offer; known location → link; renaming the set
  keeps the link
