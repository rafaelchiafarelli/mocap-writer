## 5. Moves and Renumber all rewrite the records that name scenes

- **Type:** code
- **Depends on:** 3; the first records that name scenes: film-bible
  contract/2 (bible links and per-scene values, done 2026-10-28);
  fountain-native/notes/1 (annotations) adds its anchors when it lands;
  preprod-link contract/1 (scene index) later.
- **Decided (Rafael, 2026-10-30): records follow the save.** The records
  are rewritten when the save gives the moved scenes their new numbers
  (or by Renumber all), written through the film, so the change log has
  them; Undo in the editor changes only the script, and a rewrite is taken
  back by reverting it in the change log. Not chosen: an editor undo that
  also writes the records back (it would tie the undo chain to files on
  disk).
- **Decided (Rafael, 2026-10-26, in task 1, now in git history):** a move (cut and paste)
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
