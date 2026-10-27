## 1. Notes on spans of text

- **Type:** code
- **Depends on:** io/1; scenes/1 (an annotation names its scene by
  number); file-format/layout/1 (the `annotations/` part and the
  `annotation-w-<n>` ids); an `annotation` Harpia message in
  `mocap-contracts` (its fields from film-bible contract/1, "Scene
  annotations"), done and tagged
- **Decided (Rafael, 2026-10-26):** a note is an **annotation record**
  in `<film-root>/annotations/` (layout/1's default part), and the
  Fountain text carries a marker with its **kind, id and a short text**,
  so the script stays readable in other tools. A plain note is an
  annotation of kind `note`. A span is marked with an opening and a
  closing note:
  `[[fx annotation-w-7: chuva forte]]corre pela rua[[/annotation-w-7]]`.
  An annotation on a whole element is one marker, with no closing note,
  at the element's end: `ELA corre pela rua e cai. [[fx annotation-w-7:
  chuva forte]]`. Not chosen: the id alone (other tools show bare ids);
  the whole annotation in the note (fields, states and agent proposals
  inside the script text, against the file-format decision A).
- **Contract:**
  - In: a selection of text (or an element) and "Add note"
  - Requires: the record holds kind, text, links, state and source; the
    marker's kind and short text are rewritten from the record on save,
    so the record is the source of truth for them; the editor shows the
    span highlighted and the note on hover, with the markers hidden; other
    Fountain editors still show valid notes; a marker whose record is
    missing, or a record no marker points to, is listed as a problem on
    open (layout/1), never deleted silently
  - Delivers: add/edit/remove notes on spans and elements; markers readable
    by the mocap-previz parser
- **Pre-work:** the `annotation` message above
- **Typed notes (Rafael, 2026-10-25):** the same marker carries the
  scene annotations of film-bible contract/1 (a kind such as `fx`,
  `char`, `prop`, `set`, `shot`); the kinds are fixed by the `annotation`
  message, never made up by a program.
- **Out of scope:** threads or authors on notes
- **Tests:** a span inside one line, across lines, across elements; a
  whole-element marker; removing text that holds a marker; the short text
  rewritten from the record; a missing record and an orphan record listed;
  round trip
