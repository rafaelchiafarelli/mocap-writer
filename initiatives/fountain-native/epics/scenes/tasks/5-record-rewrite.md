## 5. Moves and Renumber all rewrite the records that name scenes

- **Type:** code
- **Depends on:** 3; the first records that name scenes: film-bible
  contract/2 (bible links), fountain-native/notes/1 (annotations),
  preprod-link contract/1 (scene index). **Not ready:** no such record
  exists yet, so there is nothing to rewrite.
- **Decided (Rafael, 2026-10-26, in task 1):** a move (cut and paste)
  rewrites every record that named the old number to the new one, as one
  undoable change; Renumber all rewrites every record that names a scene;
  a copy carries no links.
- **Contract (draft, settled when the records exist):**
  - In: a cut that held numbered scenes, then a paste of it; Renumber all
  - Requires: the cut remembers its numbers; when its paste gets new
    numbers on save, the map old → new is applied to every record; the
    same map from Renumber all; one undo step with the script change.
  - Delivers: the map and its use in each record kind
- **Tests:** a moved scene's links follow it; Renumber all; undo
