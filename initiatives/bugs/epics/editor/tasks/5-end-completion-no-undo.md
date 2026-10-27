## 5. Completing with End is not undoable

- **Status:** Fixed (2026-10-27) — fixes/00008d/editor-small
- **Symptom:** Accepting an auto-completion with End replaces the line with no undo record and no re-wrap.
- **Where:** `Screenplay.moveLineEndCmd` (`trelby/screenplay.py:2583-2589`)
- **Reproduce:** type a partial character name, press End, then Undo.
- **Impact:** undo skips the change; a long completion is not re-wrapped until the next edit.
- **Likely fix:** go through the same path as Enter's completion.
