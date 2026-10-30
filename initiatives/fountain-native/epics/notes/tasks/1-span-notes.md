## 1. Notes on spans of text

- **Type:** code
- **Depends on:** io/1; scenes/1 (an annotation names its scene by
  number); file-format/layout/1 (the `annotations/` part and the
  `annotation-w-<n>` ids); an `annotation` Harpia message in
  `mocap-contracts` (its fields from film-bible contract/1, "Scene
  annotations"), done and tagged
- **Decided (Rafael, 2026-10-26):** a note is an **annotation record**
  in `<film-root>/annotations/` (layout/1's default part); a plain note is
  an annotation of kind `note`. **Nothing is written into the Fountain
  text**: the script stays a clean screenplay, so it never reads like a
  programming language and creativity is not weighed down by markup. Each
  record holds its own **anchor**: the scene number, the element in the
  scene, and the exact quoted text of the span (none for an annotation on
  a whole element), e.g. `{scene: "12.A", element: 2, quote: "corre pela
  rua"}`.
  - **A button shows the annotations** ("show me what is annotated"):
    off, the editor shows only the script; on, annotated spans are
    highlighted, elements with annotations get a mark in the margin, and
    a note shows on hover.
  - **An annotation is never lost.** If its quoted text is deleted, it
    moves to the whole element (Action line) it was in; if that element is
    deleted, it moves to the scene; if the scene is deleted, it stays on
    the scene's `OMITTED` heading (scenes/1), listed there for Rafael to
    move or discard by hand.
  - Replaces the same day's first decision, a marker in the text
    (`[[fx annotation-w-7: chuva forte]]corre pela rua[[/annotation-w-7]]`):
    with tens of annotations per scene the raw file looked like code to
    anyone opening it in another tool.
- **Contract:**
  - In: a selection of text (or an element) and "Add note"
  - Requires: the record holds kind, text, links, state, source and its
    anchor; the Fountain file is not touched (io/1's byte-identical round
    trip still holds); while editing in the writer, anchors follow the
    text as it is typed, moved or renumbered (a move rewrites the scene
    number, scenes/1); a deleted quote moves the annotation to its whole
    element, and a deleted element moves its annotations to the scene; on
    open, an anchor whose quote is no longer found (the script
    was edited in another tool) is re-found by its quote in the scene, and
    if not found it stays attached to its scene and is listed as
    **unattached** to re-attach by hand, never deleted (layout/1's
    "opening never breaks"); the show-annotations button
  - Delivers: add/edit/remove notes on spans and elements, the button, the
    anchors kept current
- **Touchpoint:** the mocap-previz parser reads the annotations from
  `annotations/`, not from the script text; its Fountain input stays plain.
- **Pre-work:** the `annotation` message above
- **Typed notes (Rafael, 2026-10-25):** the same records carry the
  scene annotations of film-bible contract/1 (a kind such as `fx`,
  `char`, `prop`, `set`, `shot`); the kinds are fixed by the `annotation`
  message, never made up by a program.
- **Out of scope:** threads or authors on notes
- **Tests:** a span inside one line, across lines, across elements; a
  whole-element annotation; typing before a span moves its anchor;
  deleting the quote moves the annotation to the element; the script
  edited outside the writer: quote re-found, or listed as unattached;
  the button on and off; the Fountain file byte-identical after
  annotating

### Decided: the `annotation` message (Rafael, 2026-10-30)

Go-ahead for `mocap-contracts` (release `v0.6.0`), and the **generic**
shape, like the bible (film-bible contract/2): an `Annotation` record
(`annotations/<id>.json`, id `annotation-<space>-<n>`) holds its `kind`
(note, character direction, prop direction, special effect, set direction,
sound direction, general direction, transition, shot), its `anchor` (scene
number, element index in the scene, the quoted text and which occurrence
of it, none for a whole element), a short `text`, who made it (`by`), and
`values`: the same `BibleValue`s as the bible (state, source, department,
by, revisit), checked against an **annotation catalog** shipped as data
(the kinds' fields of film-bible contract/1, "Scene annotations"). A shot
carries its permanent number `S<n>` per scene; the next number of each
scene is kept in `annotations/shot-counters.json`, so a number never comes
back. Not chosen: one typed message per kind (every field a schema change).
