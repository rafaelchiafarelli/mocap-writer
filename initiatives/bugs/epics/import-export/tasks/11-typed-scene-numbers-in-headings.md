## 11. A scene number typed into the heading is read as part of the place

- **Status:** Fixed (2026-10-31) — fixes/0000ae/typed-scene-numbers
- **Symptom:** A Fountain script whose headings carry their number as text,
  `.1. INT. SPACESHIP` and `.3. INT. SPACESHIP`, gets no scene numbers
  (`Line.num` stays empty, so the save numbers the scenes again) and every
  heading is a different place: Link scenes to sets offers one set per
  scene, named `1. INT. SPACESHIP`, `3. INT. SPACESHIP`, with `INT.` kept.
- **Where:** only a trailing `#n#` is a scene number when Fountain is read
  (`SCENE_NUMBER_RE`, `trelby/fountain.py:44`); a heading's place drops
  `INT.`/`EXT.` only at the start of the text (`PREFIX_RE`,
  `trelby/biblelinks.py:21`). The PDF import already reads a typed number
  (`trelby/pdfimport.py:47`).
- **Reproduce:** open a `.fountain` with the headings above in a film, save,
  then From script… → Link scenes to sets (Rafael, 2026-10-31, on a script
  converted outside the writer).
- **Impact:** scripts converted by other tools keep their numbers as text:
  the bible gets one set per scene and the numbers are not the scenes'
  identity.
- **Likely fix:** read a leading `N.` of a forced heading as its number, as
  the PDF import does; the save then writes `#N#` in place of the typed
  number (Rafael, 2026-10-31).
