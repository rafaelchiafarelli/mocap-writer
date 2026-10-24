## 1. Notes on spans of text

- **Type:** code
- **Depends on:** io/1; scenes/1 (same hidden-marker mechanism); Rafael's
  approval of the marker format
- **Contract (proposal, to confirm):**
  - In: a selection of text and "Add note"
  - Requires: Fountain has only inline notes (`[[ ]]`), so a span is marked
    with a pair of notes, `[[n:7c2e]]texto[[/n]]`, and the note's body goes
    in a `[[n:7c2e: ofegante, sem ar]]` note at the end of the scene; the
    editor shows the span highlighted and the note on hover; markers are
    hidden; other Fountain editors still show valid notes
  - Delivers: add/edit/remove span notes; notes readable by the mocap-previz
    parser
- **Pre-work:** the format above approved
- **Out of scope:** threads or authors on notes
- **Tests:** a span inside one line, across lines, across elements; removing
  text that holds a marker; round trip
