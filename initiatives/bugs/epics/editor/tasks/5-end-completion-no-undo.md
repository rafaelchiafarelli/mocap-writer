## 5. Completing with End is not undoable

- **Status:** Open
- **Symptom:** Accepting an auto-completion with End replaces the line with no undo record and no re-wrap.
- **Where:** `Screenplay.moveLineEndCmd` (`trelby/screenplay.py:2680-2686`)
- **Reproduce:** type a partial character name, press End, then Undo.
- **Impact:** undo skips the change; a long completion is not re-wrapped until the next edit.
- **Likely fix:** go through the same path as Enter's completion.
